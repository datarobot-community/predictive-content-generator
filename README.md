# Predictive Content Generator

<p align="center">
  <a href="https://app.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad9?referrerUrl=github">
    <img src="https://img.shields.io/badge/US-Open%20in%20a%20Codespace-%23909BF5?style=flat&labelColor=%2330373D" alt="US - Open in a Codespace">
  </a>
  <a href="https://app.eu.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad9?referrerUrl=github">
    <img src="https://img.shields.io/badge/EU-Open%20in%20a%20Codespace-%232BC46F?labelColor=%2330373D" alt="EU - Open in a Codespace">
  </a>
  <a href="https://app.jp.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad9?referrerUrl=github">
    <img src="https://img.shields.io/badge/JP-Open%20in%20a%20Codespace-%23EDA769?labelColor=%2330373D" alt="JP - Open in a Codespace">
  </a>
  <a href="https://app.jp.datarobot.com/usecases/application-templates/66df7eab3168a83282cf4ad9?referrerUrl=github">
    <img src="https://img.shields.io/badge/JP-%E3%80%8CCodespace%20%E3%81%A7%E9%96%8B%E3%81%8F%E3%80%8D-%23EDA769?labelColor=%2330373D" alt="JP - 「Codespaceで開く」">
  </a>
  <a href="https://join.slack.com/t/datarobot-community/shared_invite/zt-3uzfp8k50-SUdMqeux25ok9_5wr4okrg">
    <img src="https://img.shields.io/badge/%23applications-a?label=Slack&labelColor=30373D&color=81FBA6" alt="Slack #applications">
  </a>
</p>

The predictive content generator is a customizable app template for generating content using predictive model outputs. Real world use cases for this technology include:

- Using a next-best-offer predictive model to automatically draft personalized promotions.
- Using a credit risk model to automatically draft approval and rejection letters.

The predictive content generator highlights the combination of:

- Best-in-class predictive model training and deployment using DataRobot AutoML.
- Governance & hosting predictive & generative models using DataRobot MLOps.
- A shareable and customizable front-end for interacting with both predictive and
  generative models.

> [!WARNING]
> Application templates are intended to be starting points that provide guidance on how to develop, serve, and maintain AI applications.
> They require a developer or data scientist to adapt and modify them to meet business requirements before being put into production.

![Using BOB](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/bob_ui.gif)

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#-quick-start)
3. [Architecture overview](#architecture-overview)
4. [Why build AI Apps with DataRobot app templates?](#why-build-ai-apps-with-datarobot-app-templates)
5. [Make changes](#make-changes)
   - [Change the LLM](#change-the-llm)
   - [Add a new LLM](#add-a-new-llm)
   - [Change the data and model training method](#change-the-data-and-model-training-method)
   - [Modify the front-end](#modify-the-front-end)
   - [Change the language in the front-end](#change-the-language-in-the-front-end)
6. [Share results](#share-results)
7. [Delete all provisioned resources](#delete-all-provisioned-resources)
8. [Setup for advanced users](#setup-for-advanced-users)
9. [Data privacy](#data-privacy)

## Prerequisites

If you are using DataRobot Codespaces, this is already complete for you. If not, install:

- [Python](https://www.python.org/downloads/) 3.9+
- [Taskfile.dev](https://taskfile.dev/#/installation) (task runner)
- [Pulumi](https://www.pulumi.com/docs/iac/download-install/) (infrastructure as code)

## 🚀 Quick Start

### Quickstart with DataRobot CLI

#### 1. Install the DataRobot CLI

If you haven't already, install the DataRobot CLI by following the installation instructions at:  
https://github.com/datarobot-oss/cli?tab=readme-ov-file#installation

#### 2. Start the Application

Run the following command to start the Predictive Content Generator application. An interactive wizard will guide you through the selection of configuration options, including creating a `.env` file in the root directory and populating it with environment variables you specify during the wizard.

```sh
dr start
```

The DataRobot CLI (`dr`) will:
- Guide you through configuration setup
- Create and populate your `.env` file with the necessary environment variables
- Deploy your application to DataRobot
- Display a link to your running application when complete

When deployment completes, the terminal will display a link to your running application.\
👉 **Click the link to open and start using your app!**

### Build in Codespace

If you're using **DataRobot Codespace**, everything you need is already installed.
Follow the steps below to launch the entire application in just a few minutes.

Use the built-in terminal on the left sidebar of the Codespace.

From the project root:

```sh
dr start
```

When deployment completes, the terminal will display a link to your running application.\
👉 **Click the link to open and start using your app!**

### Template Development

For local development, follow all of the steps below.

#### 1. Install Pulumi (if you don't have it yet)

If Pulumi is not already installed, follow the installation instructions in the Pulumi [documentation](https://www.pulumi.com/docs/iac/download-install/).
After installing for the first time, **restart your terminal** and run:

```sh
pulumi login --local      # omit --local to use Pulumi Cloud (requires an account)
```

#### 2. Clone the Template Repository

```sh
git clone https://github.com/datarobot-community/predictive-content-generator.git
cd predictive-content-generator
```

#### 3. Create and Populate Your `.env` File
Run the following command to launch an interactive wizard that helps you create and populate your `.env` file based on `.env.template` and walks you through the required credentials setup.
```sh
dr dotenv setup
```
If you want to locate the credentials manually:

- DataRobot API Token:
  See Create a DataRobot API Key in the [DataRobot API Quickstart docs](https://docs.datarobot.com/en/docs/api/api-quickstart/index.html#create-a-datarobot-api-key).

- DataRobot Endpoint:
  See Retrieve the API Endpoint in the same [Quickstart docs](https://docs.datarobot.com/en/docs/api/api-quickstart/index.html#retrieve-the-api-endpoint).

- LLM Endpoint & API Key (Azure OpenAI):
  This template is pre-configured to use an Azure OpenAI endpoint. If you wish to use a different LLM provider, modifications to the code will be [necessary](#change-the-llm).
  Refer to the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Cjavascript-keyless%2Ctypescript-keyless%2Cpython-new&pivots=programming-language-python#retrieve-key-and-endpoint) for your resource and deployment values.

#### 4. Develop the Template

Run the following to deploy or update your application:
```bash
source set_env.sh  # On Windows use `set_env.bat`
pulumi up
```
Alternatively, run the following command for a simpler setup:

```sh
python quickstart.py YOUR_PROJECT_NAME
# Windows users may need:  py quickstart.py YOUR_PROJECT_NAME
```
Replace `YOUR_PROJECT_NAME` with any name you prefer, then press **Enter**.

When deployment completes, the terminal will display a link to your running application.\
👉 **Click the link to open and start using your app!**

**What does `quickstart.py` do?**

The quickstart script automates the entire setup process for you:

- Creates and activates a Python virtual environment
- Installs all required dependencies
- Loads your `.env` configuration
- Sets up the Pulumi stack with your project name
- Runs `pulumi up` to deploy your application
- Displays your application URL when complete

This single command replaces all the manual steps described in the [advanced setup section](#setup-for-advanced-users).

Python 3.12+ is required.

Advanced users desiring control over virtual environment creation, dependency installation, environment variable setup
and `pulumi` invocation see [here](#setup-for-advanced-users).

## Architecture overview
![Predictive content generator](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/predictive_content_architecture.svg)

App Templates contain three families of complementary logic. For this template, you can easily [modify](#make-changes) the front-end:

- **AI Logic**: Necessary to service AI requests, generate predictions, and manage predictive models.
  ```
  notebooks/  # Model training logic, scoring data prep logic
  ```
- **App Logic**: needed for user consumption; whether via a hosted frontend or integrating into an external consumption layer
  ```
  frontend/  # Streamlit frontend
  nbo/  # App biz logic & runtime helpers
  ```
- **Operational logic**: Necessary to turn on all DataRobot assets.
  ```
  infra/  # Settings for resources and assets to be created in DataRobot
  infra/__main__.py  # Pulumi program for configuring DataRobot to serve and monitor AI and App logic
  ```

## Why build AI Apps with DataRobot app templates?

App templates transform your AI projects from notebooks to production-ready applications. Too often, getting models into production means rewriting code, juggling credentials, and coordinating with multiple tools and teams just to make simple changes. DataRobot's composable AI apps framework eliminates these bottlenecks, letting you spend more time experimenting with your ML and app logic and less time wrestling with plumbing and deployment.

- Start building in minutes: Deploy complete AI applications instantly, then customize AI logic or front-end independently - no architectural rewrites needed.
- Keep working your way: Data scientists keep working in notebooks, developers in IDEs, and configs stay isolated - update any piece without breaking others.
- Iterate with confidence: Make changes locally and deploy with confidence - spend less time writing and troubleshooting plumbing, more time improving your app.

Each template provides an end-to-end AI architecture, from raw inputs to deployed application, while remaining highly customizable for specific business requirements.

## Make changes


### Change the LLM

1. Modify the `LLM` setting in `infra/settings_generative.py` by changing `LLM=GlobalLLM.AZURE_OPENAI_GPT_4_O_MINI` to any other LLM from the `GlobalLLM` object. 
     - Trial users: Please set `LLM=GlobalLLM.AZURE_OPENAI_GPT_4_O_MINI` since GPT-4o is not supported in the trial. Use the `OPENAI_API_DEPLOYMENT_ID` in `.env` to override which model is used in your azure organisation. You'll still see GPT 4o-mini in the playground, but the deployed app will use the provided azure deployment.  
2. To use an existing TextGen model or deployment:
      - In `infra/settings_generative.py`: Set `LLM=GlobalLLM.DEPLOYED_LLM`.
      - In `.env`: Set either the `TEXTGEN_REGISTERED_MODEL_ID` or the `TEXTGEN_DEPLOYMENT_ID`
      - In `.env`: Set `CHAT_MODEL_NAME` to the model name expected by the deployment (e.g. "claude-3-7-sonnet-20250219" for an anthropic deployment, "datarobot-deployed-llm" for NIM models ) 
3. In `.env`: If not using an existing TextGen model or deployment, provide the required credentials dependent on your choice.
4. Run `pulumi up` to update your stack (Or rerun your quickstart).
      ```bash
      source set_env.sh  # On windows use `set_env.bat`
      pulumi up
      ```


> **⚠️ Availability information:**  
> Using a NIM model requires custom model GPU inference, a premium feature. You will experience errors by using this type of model without the feature enabled. Contact your DataRobot representative or administrator for information on enabling this feature.

### Add a new LLM

If the LLM you want to use isn't already defined in the `LLMs` object, you can register it manually using `LLMConfig`.

1. Find the ID of the LLM you want to add by running the following in a Python session:

   ```python
   import datarobot
   print('\n'.join([i['id'] for i in datarobot.genai.LLMDefinition.list()]))
   ```

2. In `infra/settings_generative.py`, add `LLMConfig` to the existing import and register the new LLM before the `LLM =` assignment:

   ```python
   from datarobot_pulumi_utils.schema.llms import (
       LLMBlueprintArgs,
       LLMConfig,
       LLMs,
       LLMSettings,
       PlaygroundArgs,
   )

   LLMs.YOUR_LLM_NAME = LLMConfig(name="YOUR_LLM_ID", credential_type="azure")
   LLM = LLMs.YOUR_LLM_NAME
   ```

   Replace `YOUR_LLM_NAME` with a descriptive attribute name and `YOUR_LLM_ID` with the ID from step 1.

3. In `utils/credentials.py`, add a mapping from the new LLM name to its Azure deployment name inside the `get_credentials` function:

   ```python
   LLMs.YOUR_LLM_NAME.name: "YOUR_AZURE_DEPLOYMENT_NAME",
   ```

4. Run `pulumi up` to update your stack.

   ```bash
   source set_env.sh  # On windows use `set_env.bat`
   pulumi up
   ```

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
   at least once, you can also test the front-end locally using `streamlit run app.py` from the
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

#### Change the language in the front-end

Optionally, you can set the application locale in `nbo/i18n.py`, e.g. `APP_LOCALE = LanguageCode.JA`. Supported locales are Japanese and English, with English set as the default.

## Share results

1. Log into app.datarobot.com
2. Navigate to **Registry > Application**.
3. Navigate to the application you want to share, open the actions menu, and select **Share** from the dropdown.

## Delete all provisioned resources

```bash
pulumi down
```
Then run the jupyter notebook `notebooks/delete_non_pulumi_assets.ipynb`.

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
e.g., for Windows/conda/cmd.exe the previous example would change to the following:
```bash
conda create --prefix .venv pip
conda activate .\.venv
pip install -r requirements.txt
set_env.bat
pulumi stack init YOUR_PROJECT_NAME
pulumi up 
```
For projects that will be maintained, DataRobot recommends forking the repo so upstream fixes and improvements can be merged in the future.

## Data privacy
Your data privacy is important to us. Data handling is governed by the DataRobot [Privacy Policy](https://www.datarobot.com/privacy/). Review the policy before using your own data with DataRobot.
