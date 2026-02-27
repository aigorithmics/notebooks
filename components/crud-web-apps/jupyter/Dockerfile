# --- Build the backend kubeflow-wheel ---
FROM dhi.io/python:3.14.3-debian13-dev AS backend-kubeflow-wheel

WORKDIR /src

COPY ./common/backend/ .
RUN pip install --no-cache-dir setuptools wheel && \
    python3 setup.py bdist_wheel

# --- Build the frontend kubeflow library ---
FROM dhi.io/node:25.7.0-debian13-dev AS frontend-kubeflow-lib

WORKDIR /src

ENV NG_CLI_ANALYTICS="ci"
COPY ./common/frontend/kubeflow-common-lib/package.json ./
COPY ./common/frontend/kubeflow-common-lib/package-lock.json ./
RUN npm ci

COPY ./common/frontend/kubeflow-common-lib/projects ./projects
COPY ./common/frontend/kubeflow-common-lib/angular.json .
COPY ./common/frontend/kubeflow-common-lib/tsconfig.json .
RUN npm run build

# --- Build the frontend ---
FROM dhi.io/node:25.7.0-debian13-dev AS frontend

WORKDIR /src/jupyter/frontend

COPY ./jupyter/frontend/package.json ./
COPY ./jupyter/frontend/package-lock.json ./
COPY ./jupyter/frontend/tsconfig.json ./
COPY ./jupyter/frontend/tsconfig.app.json ./
COPY ./jupyter/frontend/tsconfig.spec.json ./
COPY ./jupyter/frontend/angular.json ./
COPY ./jupyter/frontend/src ./src

ENV NG_CLI_ANALYTICS="ci"
COPY --from=frontend-kubeflow-lib /src/dist/kubeflow/ ../../common/frontend/kubeflow-common-lib/dist/kubeflow/
RUN npm ci

RUN npm run build -- --output-path=./dist/default --configuration=production

# --- Build the backend environment ---
FROM dhi.io/python:3.14.3-alpine3.23-dev AS backend-env

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /package
COPY --from=backend-kubeflow-wheel /src .
RUN pip install --upgrade pip && pip install .

WORKDIR /src
COPY ./jupyter/backend/requirements.txt .
RUN pip install -r requirements.txt

# Web App
FROM dhi.io/python:3.14.3-alpine3.23

COPY --from=backend-env /venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /src

COPY ./jupyter/backend/apps/ ./apps
COPY ./jupyter/backend/entrypoint.py .

COPY --from=frontend /src/jupyter/frontend/dist/default/ /src/apps/default/static/

ENTRYPOINT ["gunicorn", "-w", "3", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "entrypoint:app"]
