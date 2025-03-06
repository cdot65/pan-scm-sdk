# HTTP Server Profiles API Issues

## Problem Summary
All HTTP server profile creation requests to the SCM API are returning 500 server errors. This appears to be an issue with the API endpoint `/config/objects/v1/http-server-profiles` rather than with the SDK implementation.

## Investigation Findings

1. We verified that the certificate_profile field in ServerModel was initially set to "None" (a string) which might cause validation issues, but correcting this to use Python's None value didn't resolve the issue.

2. We checked that the payload format being sent to the API appears to be correctly structured and follows the API schema.

3. The payload includes:
   - Proper name field
   - Correctly formatted server configurations
   - Valid container specification (folder, snippet, device)
   - Optional format settings

4. The API returns 500 errors for all variations of HTTP server profile creation:
   - HTTP servers
   - HTTPS servers
   - Multiple server profiles
   - Different container types (folder, snippet, device)

5. The API is able to successfully list and retrieve existing HTTP server profiles.

## Possible Causes

1. The API endpoint may not be fully implemented or could have a bug on the server side.
2. There may be specific validation requirements not documented in the API specification.
3. The payload structure might need additional fields or specific formatting not captured in the current model.

## Recommended Actions

1. **Contact API Support**: Since all indications point to a server-side issue, contacting Palo Alto Networks support about the `/config/objects/v1/http-server-profiles` endpoint returning 500 errors would be the most direct solution.

2. **Check API Documentation**: Verify if there are any recently published updates or known issues with this endpoint.

3. **Try Simplified Payload**: Attempt to create an HTTP server profile with a minimal payload to see if specific fields are triggering the error.

4. **Use API Explorer**: If available, test the endpoint using the Palo Alto Networks API Explorer to determine if the issue persists outside of the SDK.

5. **Monitor API Status**: Keep track of any changes or updates to the API that might resolve this issue in future releases.

## Current Workaround

Currently, the application can still list and retrieve existing HTTP server profiles, but cannot create new ones until the API endpoint issue is resolved.