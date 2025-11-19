# databricks_agent_app

A Databricks application featuring a FastAPI-based file upload service that stores files in Databricks Volumes.

## Features

- **FastAPI Web Application**: RESTful API for file management
- **File Upload**: Upload files to Databricks Volumes
- **File Management**: List, view, and delete files
- **Configurable**: Volume settings defined in `project_properties.json`
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### Run the FastAPI App Locally

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run the app
python app.py
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Test the API

```bash
# Run the example script
python examples/upload_example.py

# Or run the tests
pytest tests/test_api.py
```

See `API_README.md` for detailed API documentation.

## Getting started

0. Install UV: https://docs.astral.sh/uv/getting-started/installation/

1. Install the Databricks CLI from https://docs.databricks.com/dev-tools/cli/databricks-cli.html

2. Authenticate to your Databricks workspace, if you have not done so already:
    ```
    $ databricks configure
    ```

3. To deploy a development copy of this project, type:
    ```
    $ databricks bundle deploy --target dev
    ```
    (Note that "dev" is the default target, so the `--target` parameter
    is optional here.)

    This deploys everything that's defined for this project.
    For example, the default template would deploy a job called
    `[dev yourname] databricks_agent_app_job` to your workspace.
    You can find that job by opening your workpace and clicking on **Workflows**.

4. Similarly, to deploy a production copy, type:
   ```
   $ databricks bundle deploy --target prod
   ```

   Note that the default job from the template has a schedule that runs every day
   (defined in resources/databricks_agent_app.job.yml). The schedule
   is paused when deploying in development mode (see
   https://docs.databricks.com/dev-tools/bundles/deployment-modes.html).

5. To run a job or pipeline, use the "run" command:
   ```
   $ databricks bundle run
   ```
6. Optionally, install the Databricks extension for Visual Studio code for local development from
   https://docs.databricks.com/dev-tools/vscode-ext.html. It can configure your
   virtual environment and setup Databricks Connect for running unit tests locally.
   When not using these tools, consult your development environment's documentation
   and/or the documentation for Databricks Connect for manually setting up your environment
   (https://docs.databricks.com/en/dev-tools/databricks-connect/python/index.html).

7. For documentation on the Databricks asset bundles format used
   for this project, and for CI/CD configuration, see
   https://docs.databricks.com/dev-tools/bundles/index.html.
