import uuid
from factory import Factory, LazyFunction, Faker, SubFactory, LazyAttribute
import factory.fuzzy
from faker import Faker as FakerGenerator

from scm.models.mobile_agent.auth_settings import (
    OperatingSystem,
    MovePosition,
    AuthSettingsBaseModel,
    AuthSettingsCreateModel,
    AuthSettingsUpdateModel,
    AuthSettingsResponseModel,
    AuthSettingsMoveModel,
)

# Create a single faker instance
fake = FakerGenerator()


class AuthSettingsBaseModelFactory(Factory):
    """Factory for AuthSettingsBaseModel."""
    
    class Meta:
        model = AuthSettingsBaseModel
        
    name = Faker('pystr', min_chars=5, max_chars=30)
    authentication_profile = Faker('pystr', min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker('pybool')
    folder = "Mobile Users"


class AuthSettingsCreateModelFactory(Factory):
    """Factory for AuthSettingsCreateModel."""
    
    class Meta:
        model = AuthSettingsCreateModel
        
    name = Faker('pystr', min_chars=5, max_chars=30)
    authentication_profile = Faker('pystr', min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker('pybool')
    folder = "Mobile Users"
    
    @classmethod
    def build_valid(cls):
        """Build valid data for AuthSettingsCreateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "authentication_profile": model.authentication_profile,
            "os": model.os,
            "user_credential_or_client_cert_required": model.user_credential_or_client_cert_required,
            "folder": model.folder,
        }
    
    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid name for AuthSettingsCreateModel."""
        data = cls.build_valid()
        data["name"] = "invalid@name"
        return data
    
    @classmethod
    def build_invalid_folder(cls):
        """Build data with invalid folder for AuthSettingsCreateModel."""
        data = cls.build_valid()
        data["folder"] = "Invalid Folder"
        return data
    
    @classmethod
    def build_missing_folder(cls):
        """Build data with missing folder for AuthSettingsCreateModel."""
        data = cls.build_valid()
        del data["folder"]
        return data


class AuthSettingsResponseModelFactory(Factory):
    """Factory for AuthSettingsResponseModel."""
    
    class Meta:
        model = AuthSettingsResponseModel
        
    name = Faker('pystr', min_chars=5, max_chars=30)
    authentication_profile = Faker('pystr', min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker('pybool')
    folder = "Mobile Users"


class AuthSettingsUpdateModelFactory(Factory):
    """Factory for AuthSettingsUpdateModel."""
    
    class Meta:
        model = AuthSettingsUpdateModel
        
    name = Faker('pystr', min_chars=5, max_chars=30)
    authentication_profile = Faker('pystr', min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker('pybool')
    folder = "Mobile Users"
    
    @classmethod
    def build_valid(cls):
        """Build valid data for AuthSettingsUpdateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "authentication_profile": model.authentication_profile,
            "os": model.os,
            "user_credential_or_client_cert_required": model.user_credential_or_client_cert_required,
            "folder": model.folder,
        }
    
    @classmethod
    def build_minimal_update(cls):
        """Build minimal update data for AuthSettingsUpdateModel."""
        return {
            "authentication_profile": fake.pystr(min_chars=5, max_chars=30),
        }
    
    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid name for AuthSettingsUpdateModel."""
        data = cls.build_valid()
        data["name"] = "invalid@name"
        return data
    
    @classmethod
    def build_invalid_folder(cls):
        """Build data with invalid folder for AuthSettingsUpdateModel."""
        data = cls.build_valid()
        data["folder"] = "Invalid Folder"
        return data


class AuthSettingsMoveModelFactory(Factory):
    """Factory for AuthSettingsMoveModel."""
    
    class Meta:
        model = AuthSettingsMoveModel
        
    name = Faker('pystr', min_chars=5, max_chars=30)
    where = MovePosition.TOP
    destination = None
    
    class Params:
        """Parameters to control factory behavior."""
        needs_destination = factory.Trait(
            where=MovePosition.BEFORE,
            destination=Faker('pystr', min_chars=5, max_chars=30)
        )
    
    @classmethod
    def build_valid_before(cls):
        """Build valid data for before move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.BEFORE,
            "destination": fake.pystr(min_chars=5, max_chars=30),
        }
    
    @classmethod
    def build_valid_after(cls):
        """Build valid data for after move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.AFTER,
            "destination": fake.pystr(min_chars=5, max_chars=30),
        }
    
    @classmethod
    def build_valid_top(cls):
        """Build valid data for top move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.TOP,
        }
    
    @classmethod
    def build_valid_bottom(cls):
        """Build valid data for bottom move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.BOTTOM,
        }
    
    @classmethod
    def build_invalid_before_missing_destination(cls):
        """Build invalid data for before move with missing destination."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.BEFORE,
        }
    
    @classmethod
    def build_invalid_top_with_destination(cls):
        """Build invalid data for top move with destination."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.TOP,
            "destination": fake.pystr(min_chars=5, max_chars=30),
        }
