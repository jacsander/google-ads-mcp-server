#!/usr/bin/env python

# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Common utilities used by the MCP server."""

from typing import Any
import proto
import logging
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v21.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)

from google.ads.googleads.util import get_nested_attr
import google.auth
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from ads_mcp.mcp_header_interceptor import MCPHeaderInterceptor
import os
import importlib.resources
import json

# filename for generated field information used by search
_GAQL_FILENAME = "gaql_resources.json"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Read-only scope for Analytics Admin API and Analytics Data API.
_READ_ONLY_ADS_SCOPE = "https://www.googleapis.com/auth/adwords"


def _create_credentials() -> google.auth.credentials.Credentials:
    """Returns OAuth credentials from environment variables or Secret Manager, 
    or falls back to Application Default Credentials.
    
    Google Ads API requires OAuth 2.0 user credentials, not service accounts.
    """
    # Try to load OAuth credentials from environment variables first
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
    
    if client_id and client_secret and refresh_token:
        logger.info("Using OAuth credentials from environment variables")
        credentials = OAuthCredentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[_READ_ONLY_ADS_SCOPE]
        )
        # Refresh the token to get a valid access token
        try:
            credentials.refresh(Request())
            logger.info("Successfully refreshed OAuth credentials")
            return credentials
        except Exception as e:
            logger.error(f"Failed to refresh OAuth credentials: {e}")
            raise ValueError(f"Failed to refresh OAuth credentials: {e}. "
                           "Please verify your client_id, client_secret, and refresh_token are correct.")
    
    # Try to load from Secret Manager if available
    try:
        from google.cloud import secretmanager
        project_id = os.environ.get("GOOGLE_PROJECT_ID")
        if project_id:
            client = secretmanager.SecretManagerServiceClient()
            # Try to get OAuth credentials from Secret Manager
            try:
                secret_name = f"projects/{project_id}/secrets/google-ads-oauth-credentials/versions/latest"
                response = client.access_secret_version(request={"name": secret_name})
                oauth_creds = json.loads(response.payload.data.decode("UTF-8"))
                
                credentials = OAuthCredentials(
                    token=None,
                    refresh_token=oauth_creds.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=oauth_creds.get("client_id"),
                    client_secret=oauth_creds.get("client_secret"),
                    scopes=[_READ_ONLY_ADS_SCOPE]
                )
                credentials.refresh(Request())
                logger.info("Successfully loaded OAuth credentials from Secret Manager")
                return credentials
            except Exception as e:
                logger.warning(f"Could not load OAuth credentials from Secret Manager: {e}")
    except ImportError:
        logger.warning("google-cloud-secret-manager not available, skipping Secret Manager lookup")
    except Exception as e:
        logger.warning(f"Error accessing Secret Manager: {e}")
    
    # Fall back to Application Default Credentials (may not work for Google Ads API)
    logger.warning("No OAuth credentials found. Falling back to Application Default Credentials. "
                   "Note: Google Ads API requires OAuth 2.0 user credentials, not service accounts.")
    try:
        (credentials, _) = google.auth.default(scopes=[_READ_ONLY_ADS_SCOPE])
        return credentials
    except Exception as e:
        logger.error(f"Failed to get Application Default Credentials: {e}")
        raise ValueError(
            "Google Ads API requires OAuth 2.0 user credentials. "
            "Please set GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, and GOOGLE_ADS_REFRESH_TOKEN "
            "environment variables, or configure OAuth credentials in Secret Manager. "
            f"Error: {e}"
        )


def _get_developer_token() -> str:
    """Returns the developer token from the environment variable GOOGLE_ADS_DEVELOPER_TOKEN."""
    dev_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
    if dev_token is None:
        raise ValueError(
            "GOOGLE_ADS_DEVELOPER_TOKEN environment variable not set."
        )
    return dev_token


def _get_login_customer_id() -> str:
    """Returns login customer id, if set, from the environment variable GOOGLE_ADS_LOGIN_CUSTOMER_ID."""
    return os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")


def _get_googleads_client() -> GoogleAdsClient:
    # Use this line if you have a google-ads.yaml file
    # client = GoogleAdsClient.load_from_storage()
    client = GoogleAdsClient(
        credentials=_create_credentials(),
        developer_token=_get_developer_token(),
        login_customer_id=_get_login_customer_id(),
    )

    return client


_googleads_client = None  # Lazy initialization - created on first use


def _get_or_create_googleads_client() -> GoogleAdsClient:
    """Lazy initialization of Google Ads client.
    
    This prevents the client from being created at module import time,
    which could cause server startup failures if credentials are invalid.
    """
    global _googleads_client
    if _googleads_client is None:
        try:
            logger.info("Creating Google Ads client (first use)...")
            _googleads_client = _get_googleads_client()
            logger.info("Google Ads client created successfully")
        except Exception as e:
            logger.error(f"Failed to create Google Ads client: {e}", exc_info=True)
            raise ValueError(
                f"Failed to initialize Google Ads client: {e}. "
                "Please check your OAuth credentials and developer token."
            ) from e
    return _googleads_client


def get_googleads_service(serviceName: str) -> GoogleAdsServiceClient:
    return _get_or_create_googleads_client().get_service(
        serviceName, interceptors=[MCPHeaderInterceptor()]
    )


def get_googleads_type(typeName: str):
    return _get_or_create_googleads_client().get_type(typeName)


def format_output_value(value: Any) -> Any:
    if isinstance(value, proto.Enum):
        return value.name
    else:
        return value


def format_output_row(row: proto.Message, attributes):
    return {
        attr: format_output_value(get_nested_attr(row, attr))
        for attr in attributes
    }


def get_gaql_resources_filepath():
    package_root = importlib.resources.files("ads_mcp")
    file_path = package_root.joinpath(_GAQL_FILENAME)
    return file_path
