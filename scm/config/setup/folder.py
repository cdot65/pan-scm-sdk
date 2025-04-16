"""
Service classes for interacting with Folders in Palo Alto Networks' Strata Cloud Manager.

This module provides the Folder class for performing CRUD operations on Folder resources
in the Strata Cloud Manager.
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from scm.config import BaseObject
from scm.models.setup.folder import (
    FolderCreateModel,
    FolderResponseModel,
    FolderUpdateModel,
)


class Folder(BaseObject):
    """
    Manages Folder objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, deleting,
    and listing Folder resources through the Strata Cloud Manager API.
    """
    
    ENDPOINT = "/config/setup/v1/folders"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API
    
    def __init__(self, api_client, max_limit: int = DEFAULT_MAX_LIMIT):
        """
        Initialize the Folder service class.
        
        Args:
            api_client: The API client instance for making HTTP requests.
            max_limit: Maximum number of items to return in a single request.
                      Defaults to DEFAULT_MAX_LIMIT.
        """
        super().__init__(api_client)
        self.max_limit = min(max_limit, self.ABSOLUTE_MAX_LIMIT)
    
    def create(
        self, 
        name: str,
        parent: str,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        snippets: Optional[List[str]] = None,
    ) -> FolderResponseModel:
        """
        Create a new Folder in the Strata Cloud Manager.
        
        Args:
            name: The name of the folder.
            parent: The ID of the parent folder.
            description: Optional description of the folder.
            labels: Optional list of labels to apply to the folder.
            snippets: Optional list of snippet IDs associated with the folder.
            
        Returns:
            FolderResponseModel: The created folder.
        """
        model = FolderCreateModel(
            name=name,
            parent=parent,
            description=description,
            labels=labels,
            snippets=snippets,
        )
        
        response = super().create(model.model_dump(exclude_unset=True))
        return FolderResponseModel.model_validate(response)
    
    def get(self, folder_id: Union[str, UUID]) -> FolderResponseModel:
        """
        Get a folder by its ID.
        
        Args:
            folder_id: The ID of the folder to retrieve.
            
        Returns:
            FolderResponseModel: The requested folder.
        """
        folder_id_str = str(folder_id)
        response = super().get(folder_id_str)
        return FolderResponseModel.model_validate(response)
    
    def fetch(self, name: str, exact_match: bool = True) -> Optional[FolderResponseModel]:
        """
        Get a folder by its name.
        
        Args:
            name: The name of the folder to retrieve.
            exact_match: If True, only return folders that exactly match the name.
                        If False, return folders that contain the name.
                        
        Returns:
            Optional[FolderResponseModel]: The requested folder, or None if not found.
        """
        results = self.list(name=name, exact_match=exact_match)
        
        if not results:
            return None
            
        if exact_match:
            # When exact_match is True, filter the results to find an exact match
            for folder in results:
                if folder.name == name:
                    return folder
            return None
        else:
            # When exact_match is False, return the first result
            return results[0] if results else None
    
    def list(
        self,
        name: Optional[str] = None,
        parent: Optional[str] = None,
        max_limit: Optional[int] = None,
        exact_match: bool = False,
        **params,
    ) -> List[FolderResponseModel]:
        """
        List folders with optional filtering.
        
        Args:
            name: Filter folders by name.
            parent: Filter folders by parent ID.
            max_limit: Maximum number of items to return. Defaults to self.max_limit.
            exact_match: If True, only return folders that exactly match the name.
                        If False, return folders that contain the name.
            **params: Additional parameters to pass to the API.
            
        Returns:
            List[FolderResponseModel]: List of folders matching the filters.
        """
        # Apply API-level filtering
        if name and not exact_match:
            params["name"] = name
        if parent:
            params["parent"] = parent
            
        # Set the limit parameter
        params["limit"] = min(max_limit or self.max_limit, self.ABSOLUTE_MAX_LIMIT)
        
        # Get the results from the API
        results = super().list(**params)
        
        # Convert the results to FolderResponseModel objects
        folders = [FolderResponseModel.model_validate(item) for item in results]
        
        # Apply client-side filtering if exact_match is True and name is provided
        if name and exact_match:
            folders = [folder for folder in folders if folder.name == name]
            
        return folders
    
    def update(
        self,
        folder_id: Union[str, UUID],
        name: Optional[str] = None,
        parent: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        snippets: Optional[List[str]] = None,
    ) -> FolderResponseModel:
        """
        Update an existing folder.
        
        Args:
            folder_id: The ID of the folder to update.
            name: The new name of the folder.
            parent: The ID of the new parent folder.
            description: The new description of the folder.
            labels: The new list of labels for the folder.
            snippets: The new list of snippet IDs for the folder.
            
        Returns:
            FolderResponseModel: The updated folder.
        """
        # Get the current folder to ensure we have all required fields
        current = self.get(folder_id)
        
        # Create the update model with the current values as defaults
        model = FolderUpdateModel(
            id=UUID(str(folder_id)) if not isinstance(folder_id, UUID) else folder_id,
            name=name if name is not None else current.name,
            parent=parent if parent is not None else current.parent,
            description=description if description is not None else current.description,
            labels=labels if labels is not None else current.labels,
            snippets=snippets if snippets is not None else current.snippets,
        )
        
        # Submit the update
        response = super().update(model.model_dump(exclude_unset=True))
        return FolderResponseModel.model_validate(response)
    
    def delete(self, folder_id: Union[str, UUID]) -> None:
        """
        Delete a folder.
        
        Args:
            folder_id: The ID of the folder to delete.
        """
        folder_id_str = str(folder_id)
        super().delete(folder_id_str)
