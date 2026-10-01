from typing import Type, TypeVar, Optional, Any
from pydantic_settings import BaseSettings


SettingsT = TypeVar('SettingsT', bound=BaseSettings)


class SettingsCreateOrUpdateMixin:
    """Universal mixin for settings classes providing create_or_update method."""

    @classmethod
    def create_or_update(
            cls: Type[SettingsT],
            settings: Optional[SettingsT] = None,
            **kwargs: Any
    ) -> SettingsT:
        """
        Universal method to create new settings or update existing ones.

        Args:
            settings: Optional existing settings instance
            **kwargs: Settings to override or set

        Returns:
            Settings instance
        """
        if settings is None:
            return cls(**kwargs)

        if not kwargs:
            return settings.model_copy(deep=True)

        return settings.model_copy(update=kwargs, deep=True)
