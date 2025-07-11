# Predictive Content Generator

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

1. [Setup](#setup)
2. [Architecture overview](#architecture-overview)
3. [Why build AI Apps with DataRobot app templates?](#why-build-ai-apps-with-datarobot-app-templates)
4. [Make changes](#make-changes)
   - [Change the LLM](#change-the-llm)
   - [Change the data and model training method](#change-the-data-and-model-training-method)
   - [Modify the front-end](#modify-the-front-end)
   - [Change the language in the front-end](#change-the-language-in-the-front-end)
5. [Share results](#share-results)
6. [Delete all provisioned resources](#delete-all-provisioned-resources)
7. [Setup for advanced users](#setup-for-advanced-users)
8. [Data privacy](#data-privacy)

## Setup

> [!IMPORTANT]  
> If you are running this template in a DataRobot codespace, `pulumi` is already configured and the repository is automatically cloned;
> skip to **Step 3**.

1. If `pulumi` is not already installed, install the CLI following instructions [here](https://www.pulumi.com/docs/iac/download-install/). 
   After installing `pulumi` for the first time, restart your terminal and run:
   ```bash
   pulumi login --local  # omit --local to use Pulumi Cloud (requires separate account)
   ```

2. Clone the template repository.

   ```bash
   git clone https://github.com/datarobot-community/predictive-content-generator.git
   cd predictive-content-generator
   ```

3. Rename the file `.env.template` to `.env` in the root directory of the repo and populate your credentials.
   This template is pre-configured to use an Azure OpenAI endpoint. If you wish to use a different LLM provider, modifications to the code will be [necessary](#change-the-llm).
   Please refer to the documentation inside `.env.template`
   
4. In a terminal, run the following command:
   
   ```bash
   python quickstart.py YOUR_PROJECT_NAME  # Windows users may have to use `py` instead of `python`
   ```
   Python 3.9+ is required.

Advanced users who want to control virtual environment creation, dependency installation, environment variable setup,
and `pulumi` invocation, see [the advanced setup instructions](#setup-for-advanced-users).


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
