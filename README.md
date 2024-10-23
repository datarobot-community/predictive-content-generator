# Predictive Content Generator
Predictive Content Generator is a customizable app template for generating content using predictive model
outputs. Real world applications of this technology are:
- Using a next-best-offer predictive model to automatically draft personalized promotions
- Using a credit risk model to automatically draft approval / rejection letters

Predictive Content Genrator highlights the combination of:
* Best in class predictive model training and deployment using DataRobot AutoML
* Governance & hosting of predictive & generative models using DataRobot MLOps
* A shareable, customizable front end for interacting with both predictive and
  generative models.

![Using BOB](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/bob_ui.gif)

## Getting started
1. ```
   git clone https://github.com/datarobot/recipe-bob.git
   ```

2. Create the file `.env` in the root directory of the repo and populate your credentials.
   ```
   DATAROBOT_API_TOKEN=...
   DATAROBOT_ENDPOINT=...  # e.g. https://app.datarobot.com/api/v2
   OPENAI_API_KEY=...
   OPENAI_API_VERSION=...  # e.g. 2024-02-01
   OPENAI_API_BASE=...  # e.g. https://your_org.openai.azure.com/
   OPENAI_API_DEPLOYMENT_ID=...  # e.g. gpt-35-turbo
   PULUMI_CONFIG_PASSPHRASE=...  # required, choose an alphanumeric passphrase to be used for encrypting pulumi config
   ```
   
3. Set environment variables using your `.env` file. We have provided a helper script:
   ```
   source set_env.sh
   ```

   This script will export environment variables from `.env` and activate the virtual environment in `.venv/` (if present).

4. [Optional] Open notebook `notebooks/train_model_nbo.ipynb` and add additional models to `AppDataScienceSettings`:
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
5. Create a new stack for your project, then provision all resources.
   ```
   pulumi stack init YOUR_PROJECT_NAME
   pulumi up
   ```
   Dependencies are automatically installed in a new virtual environment located in `.venv/`.

### Details
Instructions for installing pulumi are [here][pulumi-install]. In many cases this can be done
with:
```
curl -fsSL https://get.pulumi.com | sh
pulumi login --local
```

Python must be installed for this project to run. By default, pulumi will use the python binary
aliased to `python3` to create a new virtual environment. If you wish to self-manage your virtual
environment, delete the `virtualenv` and `toolchain` keys from `Pulumi.yaml` before running `pulumi up`.


For projects that will be maintained we recommend forking the repo so upstream fixes and
improvements can be merged in the future.

[pulumi-install]: https://www.pulumi.com/docs/iac/download-install/

## Make changes
### Change the data and how the model is trained
1. Edit the notebook `notebooks/train_model_nbo.ipynb` which includes training data ingest, preparation, 
   and model training settings. The last cell of each notebook writes outputs needed for the rest of the
   pipeline and must remain.
2. Run the revised notebook.
3. Run `pulumi up` to update your stack with the changes.
4. `train_model_fraud.ipynb` and `train_model_underwriting.ipynb` contain examples of using this template
   for alternative use cases. You can run them once and call `pulumi up` to explore them.
   
   `infra/settings_main.py` can be updated to use these notebooks if you wish other collaborators to run these 
   notebooks by default when first provisioning resources.

### Change the frontend
1. Ensure you have already run `pulumi up` at least once (to provision the time series deployment)
2. Streamlit assets are in `frontend/` and can be directly edited. After provisioning the stack 
   at least once, you can also test the frontend locally using `streamlit run app.py` from the
   `frontend/` directory (don't forget to initialize your environment using `source set_env.sh`)
3. Run `pulumi up` again to update your stack with the changes.

## Delete all provisioned resources
```
pulumi down
```
