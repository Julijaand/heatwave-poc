# Project: Study on the Impact of Heat Waves on​ Hospitalizations​
The idea is to collect data​ on weather (temperature, humidity) and hospitalizations, analyze them, and predict risky ​periods to help hospitals prepare.

# Tools Used​
​To make the project simple and reproducible, we use free tools that are easy to install on a computer:​
​●​ Apache NiFi​​: Retrieves weather data (via the Internet)​​and medical data (via files), ​then sends them to the database.
​​●​ PostgreSQL avec TimescaleDB​​: Stores all data in an organized and secure ​manner.​
​●​ ​KNIME​​: Cleans the data, prepares it, and makes predictions​​(like a “brain” that ​analyzes).​
​●​ ​CloudBeaver​​: Allows you to check data with a simple ​​interface, like a spreadsheet.​
​●​ ​Apache Superset​​: Creates interactive graphs to show​​results (e.g., hospitalization​ ​curves).​

​All these tools run on a local computer, without sending data to the cloud, to ensure security.​

# Setup Environment Variables:
Create the .env file based on the provided example file `.env.example`, replace placeholders with real credentials.


# create services via docker containers using docker-compose.yml:
```sh
docker compose up -d
```

# Initialize Superset:
```sh
docker exec -it superset superset fab create-admin \
    --username admin --firstname Admin --lastname User \
    --email admin@example.com --password admin
docker exec -it superset superset db upgrade
docker exec -it superset superset init
```

# Connect to each service in a browser:
NiFi: 		https://localhost:8443/nifi
Superset: 	http://localhost:8088
CloudBeaver: 	http://localhost:8978
VS Code web: 	http://localhost:8081

login to Nifi:
docker logs nifi | grep 'Generated'
Username: 18fdcd52-7753-4753-bbb5-660672747bbe
Password: QJ90wztxYUuu3Nk32XTxMd4btMbAqzbs

login to Apache Superset:
Username: admin
Password: admin

login to CloudBeaver:
Username: postgres
Password: Postgrespw1

login to VS Code web:
Password: secretpassword

login to heatwave_db in CloudBeaver:
Username: postgres
Password: postgrespw

# Create processors in Nifi UI 
check knime_heatwave_data_cleaning_workflow.md

# Download a daily medical_data.csv (Python script) using MIMIC-III demo
```sh
# Download the two files we need (ADMISSIONS + DIAGNOSES_ICD):
wget -O ADMISSIONS.csv "https://physionet.org/files/mimiciii-demo/1.4/ADMISSIONS.csv?download"
wget -O DIAGNOSES_ICD.csv "https://physionet.org/files/mimiciii-demo/1.4/DIAGNOSES_ICD.csv?download"

#run .py script
python3 process_mimic_demo.py

##if errors occure with venv or permissions:
#Activate the venv in code-server terminal UI:
source /opt/venv/bin/activate
# Change ownership to coder:
sudo chown -R coder:coder ~/project/data/mimic_demo

```
# KNIME + Prophet not in docker, install separately:
```sh
# Download KNIME on your local desktop or the VM:

wget https://download.knime.org/analytics-platform/linux/knime-latest-linux.gtk.x86_64.tar.gz
tar -xvzf knime-latest-linux.gtk.x86_64.tar.gz

!! # KNIME Analytics Platform officially supports Python ≤ 3.11 for its scripting integration (as of version 5.5).

# KNIME officially recommends Conda for Python integration. Install Miniconda:
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh


# create the KNIME-compatible Python environment:
conda create -n knime-env -c knime -c conda-forge knime-python-scripting python=3.10

# activate it:
conda activate knime-env

# To deactivate a virtual environment,:
conda deactivate

# Check Python version (Should show Python 3.10.x)
python --version

# Install required Python packages: pandas, prophet, psycopg2-binary
conda install -c conda-forge pandas prophet psycopg2-binary

# Launch knime:
cd /home/julia/heatwave-poc/knime_5.5.1
./knime

# Verify Python Integration (in Knime UI)
File → Preferences → KNIME → Python
    # Make sure Manual points to the Conda environment binary, e.g.:
    /home/julia/miniconda3/envs/knime-env/bin/python

# automatically activate Conda and start KNIME with .sh script:
./launch_knime.sh
```


## 🧩 Troubleshooting and Lessons Learned

Throughout the implementation of the **Heatwave Prediction Dashboard**, several technical challenges emerged during the integration of **Apache Superset**, **PostgreSQL (TimescaleDB)**, and **Docker-based components**.  
Below are the main pain points and the solutions applied.

---

### 1. Database Driver Issue in Superset
**Problem:**  
Superset was unable to connect to PostgreSQL, showing the error:  
`ERROR: Could not load database driver: PostgresEngineSpec`  
Starting from **Superset 4.1.0**, database drivers like `psycopg2` are no longer bundled with the official image.
**Solution:**  
A custom `requirements-local.txt` file was created containing:
```bash
psycopg2-binary
```
It was then mounted to the correct path and after rebuilding the container, the driver was successfully installed and connections worked as expected.

### 2. NiFi GetFile Processor Not Picking Up Files
**Problem:**
The GetFile processor stayed idle (in/out/tasks = 0) and didn’t detect new CSV files.
No events appeared in Provenance or LogAttribute, even after updating or renaming the file.
**Solution:**
Replaced `GetFile` with the `ListFile` + `FetchFile` processor combination:
`ListFile` lists files from the directory (stateless and multi-node compatible).
`FetchFile` reads file content into FlowFiles for downstream processing.

### 3. Datatype Mismatch Between Database and NiFi Schema
**Problem:**
record_time was treated as text instead of a timestamp
**Solution:**
Two fixes tested:
Temporary: changed DB column to TEXT to confirm data flow.
Permanent: updated NiFi schema (JsonTreeReader) to define record_time as timestamp, keeping temperature and humidity as double.

### 4. Empty Records After Conversion (ConvertRecord Output {})
**Problem:**
ConvertRecord output was empty or contained {}.
**Solution:**
Schema mismatch — updated the JsonTreeReader and AvroRecordSetWriter schemas to exactly match the JOLT output fields.

### 5. Code-Server container didn’t have Python installed
**Problem:**
When trying to run scripts like simulate_medical.py, the codercom/code-server image lacked Python, resulting in:
```bash
bash: python3: command not found
```
**Solution:**
Build a custom code-server image extending the base one with Python and Panda. `Dockerfile` created. 
This allowed running and testing Python data scripts directly inside VS Code Web.

### 6. Data loss after rebuilding Nifi container 
**Problem:**
Losing NiFi processors / flow configuration
**Solution:**
Additional volumes mounted for Nifi container by adding them to `docker-compose.yml`.
So all processors, templates, and state survive restarts.

### 7. Incompatible Python Version for KNIME Integration
**Problem:**
KNIME Analytics Platform (as of version 5.5) officially supports Python up to version 3.11 for its scripting integration. Using newer versions (e.g., Python 3.12+) can cause compatibility issues with KNIME’s Python nodes.
**Solution:**
Create and use a KNIME-compatible Python environment (recommended via Conda):
```bash
conda create -n knime-env -c knime -c conda-forge knime-python-scripting python=3.10
```