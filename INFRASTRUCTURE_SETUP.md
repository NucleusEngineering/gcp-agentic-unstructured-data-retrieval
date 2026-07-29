
# Infrastructure Setup Guide

This guide provides a streamlined, automated process to provision the required Google Cloud infrastructure using a single command.

The `Makefile` in the root of this project contains an `infra` target that automates the following setup steps in the correct order:
1.  **Grant Permissions:** Assigns the necessary IAM roles (`AI Platform User`, `Service Usage Consumer`) to your Google Cloud user.
2.  **Create a Vertex AI Search Data Store:** Provisions the storage and indexing layer for your unstructured documents.
3.  **Create an Enterprise Search App (Engine):** Deploys the serving layer that provides advanced RAG capabilities.
4.  **Create a GCS Bucket:** Creates the Google Cloud Storage bucket required for the data ingestion pipeline.

---

## Automated Setup using `make`

This is the recommended method for setting up all required infrastructure components.

### Instructions

1.  **Configure Environment:** Ensure your `.env` file is correctly populated with your `PROJECT_ID`, `LOCATION`, `DATA_STORE_ID`, `ENGINE_ID`, and a unique `GCS_BUCKET_NAME`.
2.  **Authenticate:** Run `gcloud auth application-default login` if you haven't already to authenticate your local environment.
3.  **Run Command:** Execute the following from the project root:

<!-- end list -->

```bash
make infra
```

  * *Time Estimate: This entire process typically takes 2-3 minutes.*

The script will use the variables from your `.env` file to configure and create all the necessary resources in your Google Cloud project.

---

## Final Step: Update Application Code

Once the `make infra` command completes successfully, you must manually point your application code to the newly created Engine resource.

**Target File:** `src/search/vertex_client.py`

Find the section for `self.serving_config` and ensure the `engine` parameter is correctly reading the `ENGINE_ID` from your `.env` file.

```python
self.serving_config = self.search_client.serving_config_path(
    project=self.project_id,
    location=self.location,
    collection="default_collection",
    engine=os.getenv("ENGINE_ID"), # Ensure ENGINE_ID is in your .env
    serving_config="default_config",
)
```

-----
