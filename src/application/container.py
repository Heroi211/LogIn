from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.auth import (
    CreateApiKeyUseCase,
    GoogleLinkAccountUseCase,
    GoogleOAuthUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokenUseCase,
    RevokeApiKeyUseCase,
)
from application.use_cases.issue_auth import IssueAuthUseCase
from application.use_cases.messaging import (
    GetWhatsAppMessageStatusUseCase,
    LookupPhoneUseCase,
    NotifyAdminWhatsAppUseCase,
    SendWhatsAppMessageUseCase,
    SendWhatsAppTemplateUseCase,
)
from application.use_cases.roles import (
    CreateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListRolesUseCase,
    UpdateRoleUseCase,
)
from application.use_cases.users import (
    DeleteUserUseCase,
    ForgotPasswordUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    RegisterUserUseCase,
    ResetPasswordUseCase,
    UpdateUserUseCase,
)
from infrastructure.auth.google_oauth import GoogleOAuthService
from repositories.factory import (
    ApiKeysRepositoryFactory,
    RevokedTokensRepositoryFactory,
    RolesRepositoryFactory,
    SessionsRepositoryFactory,
    UsersRepositoryFactory,
    WhatsAppMessagingRepositoryFactory,
)


class AppContainer:
    def __init__(self, session: AsyncSession | None) -> None:
        self.session = session
        self.users = UsersRepositoryFactory.create(session)
        self.roles = RolesRepositoryFactory.create(session)
        self.sessions = SessionsRepositoryFactory.create(session)
        self.api_keys = ApiKeysRepositoryFactory.create(session)
        self.revoked_tokens = RevokedTokensRepositoryFactory.create(session)
        self.google = GoogleOAuthService()
        self.whatsapp = WhatsAppMessagingRepositoryFactory.create()

    @property
    def send_whatsapp(self) -> SendWhatsAppMessageUseCase:
        return SendWhatsAppMessageUseCase(messaging=self.whatsapp)

    @property
    def send_whatsapp_template(self) -> SendWhatsAppTemplateUseCase:
        return SendWhatsAppTemplateUseCase(messaging=self.whatsapp)

    @property
    def get_whatsapp_status(self) -> GetWhatsAppMessageStatusUseCase:
        return GetWhatsAppMessageStatusUseCase(messaging=self.whatsapp)

    @property
    def lookup_phone(self) -> LookupPhoneUseCase:
        return LookupPhoneUseCase(messaging=self.whatsapp)

    @property
    def notify_admin_whatsapp(self) -> NotifyAdminWhatsAppUseCase:
        return NotifyAdminWhatsAppUseCase(messaging=self.whatsapp)

    @property
    def issue_auth(self) -> IssueAuthUseCase:
        return IssueAuthUseCase(self.sessions, self.revoked_tokens)

    @property
    def login(self) -> LoginUserUseCase:
        return LoginUserUseCase(self.users, self.sessions, self.revoked_tokens)

    @property
    def logout(self) -> LogoutUserUseCase:
        return LogoutUserUseCase(self.sessions, self.revoked_tokens, self.users)

    @property
    def refresh(self) -> RefreshTokenUseCase:
        return RefreshTokenUseCase(self.users, self.sessions, self.revoked_tokens)

    @property
    def google_oauth(self) -> GoogleOAuthUseCase:
        return GoogleOAuthUseCase(
            self.users, self.sessions, self.revoked_tokens, google=self.google
        )

    @property
    def google_link(self) -> GoogleLinkAccountUseCase:
        return GoogleLinkAccountUseCase(self.users, self.google)

    @property
    def create_api_key(self) -> CreateApiKeyUseCase:
        return CreateApiKeyUseCase(api_keys=self.api_keys, users=self.users)

    @property
    def revoke_api_key(self) -> RevokeApiKeyUseCase:
        return RevokeApiKeyUseCase(api_keys=self.api_keys)

    @property
    def register_user(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(self.users)

    @property
    def list_users(self) -> ListUsersUseCase:
        return ListUsersUseCase(self.users)

    @property
    def get_user(self) -> GetUserUseCase:
        return GetUserUseCase(self.users)

    @property
    def update_user(self) -> UpdateUserUseCase:
        return UpdateUserUseCase(self.users)

    @property
    def delete_user(self) -> DeleteUserUseCase:
        return DeleteUserUseCase(self.users)

    @property
    def forgot_password(self) -> ForgotPasswordUseCase:
        return ForgotPasswordUseCase(self.users)

    @property
    def reset_password(self) -> ResetPasswordUseCase:
        return ResetPasswordUseCase(self.users, self.sessions, self.revoked_tokens)

    @property
    def list_roles(self) -> ListRolesUseCase:
        return ListRolesUseCase(self.roles)

    @property
    def get_role(self) -> GetRoleUseCase:
        return GetRoleUseCase(self.roles)

    @property
    def create_role(self) -> CreateRoleUseCase:
        return CreateRoleUseCase(self.roles)

    @property
    def update_role(self) -> UpdateRoleUseCase:
        return UpdateRoleUseCase(self.roles)

    @property
    def delete_role(self) -> DeleteRoleUseCase:
        return DeleteRoleUseCase(self.roles)


def get_container(session: AsyncSession | None) -> AppContainer:
    return AppContainer(session)
