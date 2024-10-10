# Recipe Best Offer Bot (BOB)
This pipeline builds a model on DataRobot and creates a front end that combines the model with a chatbot to make personalized offers to customers.

In addition to creating a hosted, shareable user interface, BOB provides:
* GenAI-focused custom metrics that automatically refresh on a schedule.
* DataRobot ML Ops hosting, monitoring, and governing the individual backend deployments.

![Using BOB](https://s3.amazonaws.com/datarobot_public/drx/recipe_gifs/bob_ui.gif)

## Getting started
1. Ensure you have the following DataRobot feature flags turned on:
   - Enable Public Network Access for all Custom Models
   - Enable Global Models in the Model Registry
   - Enable Custom Jobs
   - Enable Additional Custom Model Output in Prediction Responses

2. Create a [new][virtualenv-docs] python virtual environment with python >= 3.9.

3. Install `kedro`, create a new kedro project from this template and `cd` to the newly created directory.
   Choose a project name that is likely to be unique - DataRobot requires registered model names to be unique
   for an organization. You can change it later if necessary by editing `parameters.yml`. For authenticating with GitHub please check [here](#gh-auth).
   ```bash
   pip install kedro
   ```
   ```bash
   kedro new --name=your_project_name --starter=https://github.com/datarobot/recipe-bob --checkout main
   ```
   ```bash
   cd your_project_name
   ```
      
4. Install requirements for this template: `pip install -r requirements.txt`

5. Populate the following credentials in `conf/local/credentials.yml`:
   ```yaml
   datarobot:
     endpoint: <your endpoint>  # e.g. https://your_subdomain.datarobot.com/api/v2
     api_token: <your api token>
     prediction_environment_id: <your default prediction server id>

   azure_openai_llm_credentials:
     azure_endpoint: <your api endpoint>  # e.g. https://your_subdomain.openai.azure.com/
     api_key: <your api key>
     api_version: <your api version>
   ```

6. Run the pipeline: `kedro run`. Start exploring the pipeline using the kedro GUI: `kedro viz --include-hooks`

![Kedro Viz](https://s3.amazonaws.com/datarobot_public/drx/drx_gifs/kedro-viz.gif)

[virtualenv-docs]: https://docs.python.org/3/library/venv.html#creating-virtual-environments

## Making changes to the pipeline
The following files govern pipeline execution. In general, you will not need to modify
any other boilerplate files as you customize the pipeline.:

- `conf/base/parameters.yml`: pipeline configuration options and hyperparameters
- `conf/local/credentials.yml`: API tokens and other secrets
- `conf/base/catalog.yml`: file storage locations that can be used as node inputs or outputs,
  including locations of supporting assets to build DR custom models, execution environments
- `src/your_project_name/pipelines/*/nodes.py`: function definitions for the pipeline nodes
- `src/your_project_name/pipelines/*/pipeline.py`: node names, inputs and outputs
- `src/datarobotx/idp`: directory contains function definitions for for reusable idempotent DR nodes
- `include/your_project_name`: directory contains raw assets and templates used by the pipeline

For a deeper orientation to kedro principles and project structure visit the [Kedro][kedro-docs]
documentation.

[kedro-docs]: https://docs.kedro.org/en/stable/

### Example changes
1. Many simple pipeline configuration options can be changed by editing 
   `conf/base/parameters.yml` and then rerunning the pipeline using `kedro run`,
   e.g.:
   - Names for each created DataRobot asset
   - Modeling settings such as number of workers and advanced options
   - User selected tones for input to the Chatbot

2. Assets and templates needed to build DR custom models, execution environments, and
   custom apps can generally be found in the respective `include/your_project_name` subdirectories
   and can be edited to e.g. tailor the look and feel of the streamlit app; as with any
   other change just call `kedro run` to rerun the pipeline and incorporate changes.

3. Update function definitions in `nodes.py` to change the actual logic for
   a step in the pipeline or to define a new node, e.g.:
   - `prepare_dataset_for_modeling()`: is an empty function that can be filled with
     logic to prepare the dataset for modeling prior to loading into DataRobot.

### Debugging your front end
If you want to change the streamlit app take the following steps:
1. Run the pipeline (`kedro run`).
2. `cd` into `include/your_project_name/app`.
3. `streamlit run app.py`. The app will run using the same files and dependencies it will have when deployed.

## <a name="gh-auth"></a> Authenticating with GitHub
How to install `gh` [GitHub CLI][GitHub CLI-link] 

[GitHub CLI-link]: https://github.com/cli/cli

Run `gh auth login` in the terminal and answer the following questions with:
- `? What account do you want to log into?` **GitHub.com**
- `? What is your preferred protocol for Git operations on this host?` **HTTPS**
- `? Authenticate Git with your GitHub credentials?` **Yes**
- `? How would you like to authenticate GitHub CLI?` **Login with a web browser**

Copy the code in: `! First copy your one-time code:` **XXXX-XXXX**

Open a web browser at https://github.com/login/device and enter the above code manually.

You should see in the terminal:
- `✓ Authentication complete.`
- `✓ Logged in as YOUR_USERNAME`

More details on GitHub authentication [here][gh-docs].

[gh-docs]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github#https


## Running the pipeline without `kedro new`

If you are making changes to the codebase or constructing your own template, then the cycle of running `kedro new`, testing changes on the instantiated pipeline and copying the changes over to the core template can be inconvenient. For faster development, take the following steps:
1. Clone the repository.
2. Create a virtual environment and install the requirements: `pip install -r requirements.txt`.
3. Add your credentials to `recipe-bob/conf/local/credentials.yml`.
4. Add a file to `recipe-bob/conf/base/globals.yml` with the following content:
   ```yaml
   project_name: your_project_name  # Overrides "${globals:project_name}" in parameters.yml
   source: # One of nbo | underwriting | fraud_monitoring
   ```
5. Copy the `datarobotx` folder containing the idp helpers into the `recipe-bob/src` folder of the recipe template. You can find these by instantiating a new project with `kedro new`.
6. When you are finished, it is usually a good idea to execute `kedro run -p delete_assets`. This will remove DataRobot assets created during the pipeline run and unclutter your DataRobot instance.