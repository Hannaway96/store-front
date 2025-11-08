### Description of Changes

This pull request introduces the following updates to the `store-front` repository:

1. **API Documentation**:
   - Added comprehensive documentation for the API endpoints.

2. **User Management Features**:
   - Implemented registration functionality.
   - Added login API for user authentication.
   - Introduced refresh token support to ensure seamless user sessions.

3. **Update to Testing Method**:
   - Updated the testing method to use `docker compose run api pytest` for running the test suite.

### Summary of Changes

- **Lines Added**: 355
- **Lines Deleted**: 108
- **Total Files Changed**: 13
- **Commits Included**: 3

### Testing and Verification

Please ensure the following:
- Test the API endpoints to verify functionality based on the new documentation.
- Confirm that user registration, login, and token refreshing operate without issues.
- Use the updated testing method:
  - Run the test suite using `docker compose run api pytest` to ensure all changes and features are covered.
- Check for backward compatibility with pre-existing code.

### Additional Notes

This is ready for review and, if approved, can be merged into the `main` branch as the code has been verified clean and mergeable.
