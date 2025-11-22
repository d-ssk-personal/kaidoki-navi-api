"""
アカウント管理サービス
ビジネスロジックを担当
"""
from typing import Dict, Any, List, Tuple, Optional
from admin.repositories.admin_repository import AdminRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class AccountService:
    """アカウント管理のビジネスロジック"""

    def __init__(self):
        self.admin_repo = AdminRepository()

    def list_accounts(
        self,
        filters: Dict[str, Any],
        page: int,
        limit: int,
        admin: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        アカウント一覧を取得（権限チェック付き）

        Args:
            filters: フィルター条件
            page: ページ番号
            limit: 1ページあたりの件数
            admin: リクエストした管理者の情報

        Returns:
            (アカウントリスト, 総件数, 総ページ数)
        """
        # 権限に応じてフィルターを調整
        if admin['role'] == 'company_admin':
            # 企業管理者は自社のアカウントのみ表示
            filters['companyId'] = admin.get('companyId')
        elif admin['role'] == 'store_user':
            # 店舗ユーザーは自分のアカウントのみ表示
            filters['adminId'] = admin.get('admin_id')

        accounts, total = self.admin_repo.list_accounts(filters, page, limit)

        # 店舗ユーザーの場合、自分のアカウント以外をフィルタリング
        if admin['role'] == 'store_user':
            accounts = [acc for acc in accounts if acc.get('adminId') == admin.get('admin_id')]
            total = len(accounts)

        total_pages = (total + limit - 1) // limit if total > 0 else 1

        return accounts, total, total_pages

    def get_account(
        self,
        admin_id: str,
        requesting_admin: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        アカウント詳細を取得（権限チェック付き）

        Args:
            admin_id: アカウントID
            requesting_admin: リクエストした管理者の情報

        Returns:
            アカウント情報（見つからない場合はNone）

        Raises:
            ValueError: 権限がない場合
        """
        account = self.admin_repo.get_by_id(admin_id)

        if not account:
            return None

        # 権限チェック
        if not self._check_permission(requesting_admin, account):
            raise ValueError("このアカウントにアクセスする権限がありません")

        # パスワードハッシュを削除
        if 'passwordHash' in account:
            del account['passwordHash']

        return account

    def create_account(
        self,
        account_data: Dict[str, Any],
        requesting_admin: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        アカウントを作成（権限チェック付き）

        Args:
            account_data: アカウントデータ
            requesting_admin: リクエストした管理者の情報

        Returns:
            作成されたアカウント情報

        Raises:
            ValueError: 権限がない場合、またはバリデーションエラー
        """
        # 権限チェック
        if requesting_admin['role'] == 'company_admin':
            # 企業管理者は自社のアカウントのみ作成可能
            if account_data.get('role') == 'system_admin':
                raise ValueError("企業管理者はシステム管理者を作成できません")
            if account_data.get('companyId') != requesting_admin.get('company_id'):
                raise ValueError("他社のアカウントは作成できません")
        elif requesting_admin['role'] == 'store_user':
            raise ValueError("店舗ユーザーはアカウントを作成できません")

        # ユーザー名の重複チェック
        existing = self.admin_repo.get_by_username(account_data['username'])
        if existing:
            raise ValueError("このユーザー名は既に使用されています")

        # 必須フィールドの検証
        if account_data['role'] in ['company_admin', 'store_user']:
            if not account_data.get('companyId'):
                raise ValueError("企業IDは必須です")

        if account_data['role'] == 'store_user':
            if not account_data.get('storeId'):
                raise ValueError("店舗IDは必須です")

        # アカウントを作成
        account = self.admin_repo.create_account(account_data)
        logger.info(f"Created account: {account.get('adminId')}")

        return account

    def update_account(
        self,
        admin_id: str,
        account_data: Dict[str, Any],
        requesting_admin: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        アカウントを更新（権限チェック付き）

        Args:
            admin_id: アカウントID
            account_data: 更新データ
            requesting_admin: リクエストした管理者の情報

        Returns:
            更新されたアカウント情報（見つからない場合はNone）

        Raises:
            ValueError: 権限がない場合
        """
        # 既存アカウントの確認
        existing_account = self.admin_repo.get_by_id(admin_id)
        if not existing_account:
            return None

        # 権限チェック
        if not self._check_permission(requesting_admin, existing_account):
            raise ValueError("このアカウントを更新する権限がありません")

        # 企業管理者の制限
        if requesting_admin['role'] == 'company_admin':
            # 役割をsystem_adminに変更することはできない
            if account_data.get('role') == 'system_admin':
                raise ValueError("企業管理者はシステム管理者を作成できません")
            # 他社への変更はできない
            if account_data.get('companyId') and account_data['companyId'] != requesting_admin.get('company_id'):
                raise ValueError("他社のアカウントには変更できません")

        # アカウントを更新
        updated_account = self.admin_repo.update_account(admin_id, account_data)

        if updated_account:
            logger.info(f"Updated account: {admin_id}")

        return updated_account

    def delete_account(
        self,
        admin_id: str,
        requesting_admin: Dict[str, Any]
    ) -> bool:
        """
        アカウントを削除（権限チェック付き）

        Args:
            admin_id: アカウントID
            requesting_admin: リクエストした管理者の情報

        Returns:
            削除成功ならTrue、見つからない場合はFalse

        Raises:
            ValueError: 権限がない場合、または自分自身を削除しようとした場合
        """
        # 自分自身の削除を防ぐ
        if admin_id == requesting_admin.get('admin_id'):
            raise ValueError("自分自身のアカウントは削除できません")

        # 既存アカウントの確認
        existing_account = self.admin_repo.get_by_id(admin_id)
        if not existing_account:
            return False

        # 権限チェック
        if not self._check_permission(requesting_admin, existing_account):
            raise ValueError("このアカウントを削除する権限がありません")

        # アカウントを削除
        success = self.admin_repo.delete_account(admin_id)

        if success:
            logger.info(f"Deleted account: {admin_id}")

        return success

    def _check_permission(
        self,
        requesting_admin: Dict[str, Any],
        target_account: Dict[str, Any]
    ) -> bool:
        """
        リクエストした管理者が対象アカウントにアクセス権限があるかチェック

        Args:
            requesting_admin: リクエストした管理者の情報
            target_account: 対象アカウントの情報

        Returns:
            権限がある場合True
        """
        # システム管理者は全てのアカウントにアクセス可能
        if requesting_admin['role'] == 'system_admin':
            return True

        # 企業管理者は自社のアカウントにのみアクセス可能
        if requesting_admin['role'] == 'company_admin':
            return target_account.get('companyId') == requesting_admin.get('company_id')

        # 店舗ユーザーは自分のアカウントにのみアクセス可能
        if requesting_admin['role'] == 'store_user':
            return target_account.get('adminId') == requesting_admin.get('admin_id')

        return False
