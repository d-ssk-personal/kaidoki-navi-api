#!/usr/bin/env python3
"""
template.yamlからDynamoDBテーブル定義を読み取り、
ローカル開発用のinit-dynamodb.shを自動生成するスクリプト

このスクリプトにより、テーブル定義はtemplate.yamlで一元管理されます。
"""

import yaml
import json
import re
from typing import Dict, Any, List


# CloudFormationカスタムタグのコンストラクタを定義
def sub_constructor(loader, node):
    """!Sub タグのコンストラクタ"""
    return {'Fn::Sub': loader.construct_scalar(node)}


def ref_constructor(loader, node):
    """!Ref タグのコンストラクタ"""
    return {'Ref': loader.construct_scalar(node)}


def get_att_constructor(loader, node):
    """!GetAtt タグのコンストラクタ"""
    return {'Fn::GetAtt': loader.construct_sequence(node)}


# カスタムローダーを作成
class CFNLoader(yaml.SafeLoader):
    pass


# カスタムタグを登録
CFNLoader.add_constructor('!Sub', sub_constructor)
CFNLoader.add_constructor('!Ref', ref_constructor)
CFNLoader.add_constructor('!GetAtt', get_att_constructor)


def load_template() -> Dict[str, Any]:
    """template.yamlを読み込む"""
    with open('template.yaml', 'r') as f:
        return yaml.load(f, Loader=CFNLoader)


def extract_table_name(table_name_def: Any) -> str:
    """
    CloudFormationのテーブル名定義からベース名を抽出
    例: !Sub chirashi-kitchen-articles-${Environment} -> chirashi-kitchen-articles
    """
    if isinstance(table_name_def, str):
        # 単純な文字列の場合
        return table_name_def.replace('-${Environment}', '')
    elif isinstance(table_name_def, dict) and 'Fn::Sub' in table_name_def:
        # !Sub の場合
        sub_value = table_name_def['Fn::Sub']
        # ${Environment} を削除
        return sub_value.replace('-${Environment}', '')
    else:
        # その他の形式
        return str(table_name_def).replace('-${Environment}', '')


def convert_attribute_type(cf_type: str) -> str:
    """CloudFormation属性タイプをDynamoDB CLIタイプに変換"""
    return cf_type  # S, N, B はそのまま使える


def generate_gsi_json(indexes: List[Dict]) -> str:
    """GlobalSecondaryIndexesをJSON文字列として生成"""
    gsi_list = []

    for index in indexes:
        gsi = {
            "IndexName": index['IndexName'],
            "KeySchema": [
                {
                    "AttributeName": key['AttributeName'],
                    "KeyType": key['KeyType']
                }
                for key in index['KeySchema']
            ],
            "Projection": index['Projection']
        }
        gsi_list.append(gsi)

    return json.dumps(gsi_list, ensure_ascii=False)


def generate_table_creation_command(table_name: str, table_def: Dict[str, Any]) -> str:
    """テーブル作成用のAWS CLIコマンドを生成"""
    props = table_def['Properties']

    # 属性定義
    attr_defs = ' \\\n    '.join([
        f"AttributeName={attr['AttributeName']},AttributeType={attr['AttributeType']}"
        for attr in props['AttributeDefinitions']
    ])

    # キースキーマ
    key_schema_parts = []
    for key in props['KeySchema']:
        key_schema_parts.append(f"AttributeName={key['AttributeName']},KeyType={key['KeyType']}")

    # テーブル表示名
    display_name = table_name.replace('chirashi-kitchen-', '').replace('-', ' ').title()

    # コマンドの開始
    cmd = f'''# {display_name}テーブル
echo "Creating {table_name} table..."
aws dynamodb create-table \\
  --table-name {table_name} \\
  --attribute-definitions \\
    {attr_defs} \\
  --key-schema {' '.join(key_schema_parts)} \\
  --billing-mode PAY_PER_REQUEST'''

    # GSIがある場合
    if 'GlobalSecondaryIndexes' in props:
        gsi_json = generate_gsi_json(props['GlobalSecondaryIndexes'])
        # JSONを1行で表現（シェルスクリプト内で改行を避ける）
        gsi_json_compact = gsi_json.replace('\n', ' ').replace('  ', ' ')
        cmd += f''' \\
  --global-secondary-indexes \\
    '{gsi_json_compact}' '''

    cmd += f'''\\
  --endpoint-url $ENDPOINT \\
  --region $REGION \\
  --no-cli-pager 2>/dev/null || echo "{table_name} table already exists"
'''

    return cmd


def generate_init_script(template: Dict[str, Any]) -> str:
    """init-dynamodb.shの内容を生成"""

    script = '''#!/bin/bash

# DynamoDB Local テーブル初期化スクリプト
# このファイルは自動生成されています
# 手動で編集しないでください
# 生成元: template.yaml
# 生成スクリプト: scripts/generate_init_script.py

ENDPOINT="http://localhost:8000"
REGION="ap-northeast-1"

echo "DynamoDB Localのテーブルを作成します..."
echo "(テーブル定義はtemplate.yamlから自動生成されています)"
echo ""

'''

    resources = template.get('Resources', {})

    # DynamoDBテーブルのみを抽出
    tables = {
        name: resource
        for name, resource in resources.items()
        if resource.get('Type') == 'AWS::DynamoDB::Table'
    }

    # テーブル作成コマンドを生成
    for table_resource_name, table_def in tables.items():
        table_name = extract_table_name(table_def['Properties']['TableName'])
        cmd = generate_table_creation_command(table_name, table_def)
        script += cmd + '\n'

    script += '''
echo ""
echo "テーブル一覧:"
aws dynamodb list-tables --endpoint-url $ENDPOINT --region $REGION --no-cli-pager

echo ""
echo "DynamoDB Local の初期化が完了しました！"
echo "管理UI: http://localhost:8002"
'''

    return script


def main():
    """メイン処理"""
    print("📖 template.yamlを読み込んでいます...")
    template = load_template()

    print("🔄 init-dynamodb.shを生成しています...")
    script_content = generate_init_script(template)

    print("💾 scripts/init-dynamodb.shに書き込んでいます...")
    with open('scripts/init-dynamodb.sh', 'w') as f:
        f.write(script_content)

    print("✅ 完了しました！")
    print("")
    print("テーブル定義はtemplate.yamlで一元管理されています。")
    print("テーブル定義を変更した場合は、このスクリプトを再実行してください：")
    print("  python scripts/generate_init_script.py")


if __name__ == '__main__':
    main()
