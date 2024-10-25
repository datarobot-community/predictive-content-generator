# Predictive content generator

The predictive content generator is a customizable app template for generating content using predictive model outputs. Real world applications of this technology include:

- Using a next-best-offer predictive model to automatically draft personalized promotions.
- Using a credit risk model to automatically draft approval and rejection letters.

The predictive content generator highlights the combination of:

- Best-in-class predictive model training and deployment using DataRobot AutoML.
- Governance & hosting predictive & generative models using DataRobot MLOps.
- A shareable and customizable front-end for interacting with both predictive and
  generative models.

![Using BOB](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/bob_ui.gif)

## Setup

1. To start using this template, first clone the repository.

   ```
   git clone https://github.com/datarobot-community/predictive-content-generator.git
   ```

2. Create the file `.env` in the root directory of the repository and provide your credentials.
   
   ```
   DATAROBOT_API_TOKEN=...
   DATAROBOT_ENDPOINT=...  # e.g. https://app.datarobot.com/api/v2
   OPENAI_API_KEY=...
   OPENAI_API_VERSION=...  # e.g. 2024-02-01
   OPENAI_API_BASE=...  # e.g. https://your_org.openai.azure.com/
   OPENAI_API_DEPLOYMENT_ID=...  # e.g. gpt-35-turbo
   PULUMI_CONFIG_PASSPHRASE=...  # required, choose an alphanumeric passphrase to be used for encrypting pulumi config
   ```
   
3. Set environment variables using the `.env` file. DataRobot has provided a helper script below:
   ```
   source set_env.sh
   # on Windows: set_env.bat or Set-Env.ps1
   ```
   
   This script exports environment variables from `.env` and activates the virtual 
   environment in `.venv/` (if present).

4. Optional. Open the notebook `notebooks/train_model_nbo.ipynb` and add additional models to `AppDataScienceSettings`:

   ```
      models=[
         ...
         LLMModelSpec(
            name="gpt-4",
            input_price_per_1k_tokens=0.003,
            output_price_per_1k_tokens=0.004,
         ),
         ...
      ],
   ```

6. If you're a first-time user, install the Pulumi CLI by following the instructions [here](#details) before proceeding with this workflow.

7. Create a new stack for your project (update the placeholder `YOUR_PROJECT_NAME`).

   ```
   pulumi stack init YOUR_PROJECT_NAME
   ```

8. Provision all resources and install dependencies in a new virtual environment located in `.venv/`

   ```
   pulumi up
   ```

### Details

Instructions for installing Pulumi are [here](https://www.pulumi.com/docs/iac/download-install/). In many cases this can be done
with:

```
curl -fsSL https://get.pulumi.com | sh
pulumi login --local
```

Restart your terminal.

```
source set_env.sh
# on Windows: set_env.bat or Set-Env.ps1
```

Python must be installed for this project to run. By default, pulumi will use the Python binary aliased to `python3` to create a new virtual environment. If you wish to self-manage your virtual environment, delete the `virtualenv` and `toolchain` keys from `Pulumi.yaml` before running `pulumi up`. For projects that will be maintained, DataRobot recommends forking the repo so upstream fixes and improvements can be merged in the future.

### Feature flags

This app template requires certain feature flags to be enabled or disabled in your DataRobot account. The required feature flags can be found in [infra/feature_flag_requirements.yaml](infra/feature_flag_requirements.yaml). Contact your DataRobot representative or administrator for information on enabling the feature.

## Architecture Overview
![Predictive content generator](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/predictive_content_architecture.svg)

## Make changes

### Change the data and model training method

1. Edit the notebook `notebooks/train_model_nbo.ipynb` which includes steps to import and prepare training data and configure settings to train models. The last cell of each notebook is required for the rest of the pipeline.
2. Run the revised notebook.
3. Run `pulumi up` to update your stack with the changes.
4. `train_model_fraud.ipynb` and `train_model_underwriting.ipynb` contain examples using this template for alternative use cases. You can run them once and call `pulumi up` to explore them. `infra/settings_main.py` can be updated to use these notebooks if you wish other collaborators to run these notebooks by default when first provisioning resources.

### Modify the front-end

1. Ensure you have already run `pulumi up` at least once (to provision the time series deployment).
2. Streamlit assets are in `frontend/` and can be directly edited. After provisioning the stack 
   at least once, you can also test the frontend locally using `streamlit run app.py` from the
   `frontend/` directory (don't forget to initialize your environment using `source set_env.sh`).
3. Run `pulumi up` again to update your stack with the changes.

## Share results

1. Log into app.datarobot.com
2. Navigate to **Registry > Application**.
3. Navigate to the application you want to share, open the actions menu, and select **Share** from the dropdown.

## Delete all provisioned resources

```
pulumi down
```
