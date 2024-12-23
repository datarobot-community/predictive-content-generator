# Predictive Content Generator

The predictive content generator is a customizable app template for generating content using predictive model outputs. Real world applications of this technology include:

- Using a next-best-offer predictive model to automatically draft personalized promotions.
- Using a credit risk model to automatically draft approval and rejection letters.

The predictive content generator highlights the combination of:

- Best-in-class predictive model training and deployment using DataRobot AutoML.
- Governance & hosting predictive & generative models using DataRobot MLOps.
- A shareable and customizable front-end for interacting with both predictive and
  generative models.

> [!WARNING]
> Application Templates are intended to be starting points that provide guidance on how to develop, serve, and maintain AI applications.
> They require a developer or data scientist to adapt, and modify them to business requirements before being put into production.

![Using BOB](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/bob_ui.gif)

## Table of Contents
1. [Setup](#setup)
2. [Architecture Overview](#architecture-overview)
3. [Why Build AI Apps with DataRobot App Templates?](#why-build-ai-apps-with-datarobot-app-templates)
4. [Make Changes](#make-changes)
   - [Change the Data and Model Training Method](#change-the-data-and-model-training-method)
   - [Modify the Frontend](#modify-the-front-end)
   - [Change the Language in the Frontend](#change-the-language-in-the-frontend)
5. [Share Results](#share-results)
6. [Delete All Resources](#delete-all-provisioned-resources)
7. [Setup for Advanced Users](#setup-for-advanced-users)
8. [Data Privacy](#data-privacy)

## Setup

> [!IMPORTANT]  
> If you are running in DataRobot Codespaces, `pulumi` is already configured and the repo automatically cloned;
> please skip to **Step 3**.

1. If `pulumi` is not already installed, install the CLI following instructions [here](https://www.pulumi.com/docs/iac/download-install/). 
   After installing for the first time, restart your terminal and run:
   ```bash
   pulumi login --local  # omit --local to use Pulumi Cloud (requires separate account)
   ```

2. Clone the template repository.

   ```bash
   git clone https://github.com/datarobot-community/predictive-content-generator.git
   cd predictive-content-generator
   ```

3. Rename the file `.env.template` to `.env` in the root directory of the repo and populate your credentials.
   This template is pre-configured to use an Azure OpenAI endpoint. If you wish to use a different LLM provider, modifications to the code will be necessary.

   ```bash
   DATAROBOT_API_TOKEN=...
   DATAROBOT_ENDPOINT=...  # e.g. https://app.datarobot.com/api/v2
   OPENAI_API_KEY=...
   OPENAI_API_VERSION=...  # e.g. 2024-02-01
   OPENAI_API_BASE=...  # e.g. https://your_org.openai.azure.com/
   OPENAI_API_DEPLOYMENT_ID=...  # e.g. gpt-35-turbo
   PULUMI_CONFIG_PASSPHRASE=...  # required, choose an alphanumeric passphrase to be used for encrypting pulumi config
   ```
   Use the following resources to locate the required credentials:
   - **DataRobot API Token**: Refer to the *Create a DataRobot API Key* section of the [DataRobot API Quickstart docs](https://docs.datarobot.com/en/docs/api/api-quickstart/index.html#create-a-datarobot-api-key).
   - **DataRobot Endpoint**: Refer to the *Retrieve the API Endpoint* section of the same [DataRobot API Quickstart docs](https://docs.datarobot.com/en/docs/api/api-quickstart/index.html#retrieve-the-api-endpoint).
   - **LLM Endpoint and API Key**: Refer to the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Cjavascript-keyless%2Ctypescript-keyless%2Cpython-new&pivots=programming-language-python#retrieve-key-and-endpoint).

   
4. In a terminal run:
   ```bash
   python quickstart.py YOUR_PROJECT_NAME  # Windows users may have to use `py` instead of `python`
   ```

Advanced users desiring control over virtual environment creation, dependency installation, environment variable setup
and `pulumi` invocation see [here](#setup-for-advanced-users).


## Architecture Overview
![Predictive content generator](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/predictive_content_architecture.svg)

App Templates contain three families of complementary logic. For this template you can [opt-in](#make-changes) to fully 
custom AI logic and a fully custom frontend or utilize DR's off the shelf offerings:
- **AI Logic**: needed to service AI requests, generate predictions, and manage predictive models.
  ```
  notebooks/  # Model training logic, scoring data prep logic
  deployment_generative/  # Simple monitored LLM deployment
  ```
- **App Logic**: needed for user consumption; whether via a hosted frontend or integrating into an external consumption layer
  ```
  frontend/  # Streamlit frontend
  nbo/  # App biz logic & runtime helpers
  ```
- **Operational Logic**: needed to turn it all on
  ```
  __main__.py  # Pulumi program for configuring DR to serve and monitor AI & App logic
  infra/  # Settings for resources and assets created in DR
  ```

## Why build AI Apps with DataRobot App Templates?

App Templates transform your AI projects from notebooks to production-ready applications. Too often, getting models into production means rewriting code, juggling credentials, and coordinating with multiple tools & teams just to make simple changes. DataRobot's composable AI apps framework eliminates these bottlenecks, letting you spend more time experimenting with your ML and app logic and less time wrestling with plumbing and deployment.
- Start Building in Minutes: Deploy complete AI applications instantly, then customize AI logic or frontend independently - no architectural rewrites needed.
- Keep Working Your Way: Data scientists keep working in notebooks, developers in IDEs, and configs stay isolated - update any piece without breaking others.
- Iterate With Confidence: Make changes locally and deploy with confidence - spend less time writing and troubleshooting plumbing, more time improving your app.

Each template provides an end-to-end AI architecture, from raw inputs to deployed application, while remaining highly customizable for specific business requirements.

## Make changes

### Change the data and model training method

1. Edit the notebook `notebooks/train_model_nbo.ipynb` which includes steps to import and prepare training data and configure settings to train models. The last cell of each notebook is required for the rest of the pipeline.
2. Run the revised notebook.
3. Run `pulumi up` to update your stack with the changes.
```bash
source set_env.sh  # On windows use `set_env.bat`
pulumi up
```
4. `train_model_fraud.ipynb` and `train_model_underwriting.ipynb` contain examples using this template for alternative use cases. You can run them once and call `pulumi up` to explore them. `infra/settings_main.py` can be updated to use these notebooks if you wish other collaborators to run these notebooks by default when first provisioning resources.

### Modify the front-end

1. Ensure you have already run `pulumi up` at least once (to provision the deployment).
2. Streamlit assets are in `frontend/` and can be directly edited. After provisioning the stack 
   at least once, you can also test the frontend locally using `streamlit run app.py` from the
   `frontend/` directory (don't forget to initialize your environment using `source set_env.sh`).
```bash
source set_env.sh  # On windows use `set_env.bat`
cd frontend
streamlit run app.py
```
3. Run `pulumi up` again to update your stack with the changes.
```bash
source set_env.sh  # On windows use `set_env.bat`
pulumi up
```

#### Change the language in the frontend
Optionally, you can set the application locale in `nbo/i18n.py`, e.g. `APP_LOCALE = LanguageCode.JA`. Supported locales are Japanese and English, with English set as the default.

## Share results

1. Log into app.datarobot.com
2. Navigate to **Registry > Application**.
3. Navigate to the application you want to share, open the actions menu, and select **Share** from the dropdown.

## Delete all provisioned resources

```bash
pulumi down
```
Then run the jupyter notebook `notebooks/delete_non_pulumi_assets.ipynb`

## Setup for advanced users
For manual control over the setup process adapt the following steps for MacOS/Linux to your environent:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
source set_env.sh
pulumi stack init YOUR_PROJECT_NAME
pulumi up 
```
e.g. for Windows/conda/cmd.exe this would be:
```bash
conda create --prefix .venv pip
conda activate .\.venv
pip install -r requirements.txt
set_env.bat
pulumi stack init YOUR_PROJECT_NAME
pulumi up 
```
For projects that will be maintained, DataRobot recommends forking the repo so upstream fixes and improvements can be merged in the future.

## Data Privacy
Your data privacy is important to us. Data handling is governed by the DataRobot [Privacy Policy](https://www.datarobot.com/privacy/), please review before using your own data with DataRobot.
