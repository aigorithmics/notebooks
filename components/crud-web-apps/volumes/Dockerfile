# --- Build the backend kubeflow-wheel ---
FROM python:3.14.3-slim-bookworm AS backend-kubeflow-wheel

WORKDIR /src

COPY ./common/backend/ .
RUN pip install --no-cache-dir setuptools wheel && \
    python3 setup.py bdist_wheel

# --- Build the frontend kubeflow library ---
FROM node:24.14.0-bookworm AS frontend-kubeflow-lib

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
FROM node:24.14.0-bookworm AS frontend

WORKDIR /src/volumes/frontend

COPY ./volumes/frontend/package.json ./
COPY ./volumes/frontend/package-lock.json ./
COPY ./volumes/frontend/tsconfig.json ./
COPY ./volumes/frontend/tsconfig.app.json ./
COPY ./volumes/frontend/tsconfig.spec.json ./
COPY ./volumes/frontend/angular.json ./
COPY ./volumes/frontend/src ./src

ENV NG_CLI_ANALYTICS="ci"
COPY --from=frontend-kubeflow-lib /src/dist/kubeflow/ ../../common/frontend/kubeflow-common-lib/dist/kubeflow/
RUN npm ci

RUN npm run build -- --output-path=./dist/default --configuration=production

# Web App
FROM python:3.14.3-alpine3.23

WORKDIR /package
COPY --from=backend-kubeflow-wheel /src .
RUN pip install --upgrade pip && pip install . 

WORKDIR /src
COPY ./volumes/backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./volumes/backend/apps/ ./apps
COPY ./volumes/backend/entrypoint.py .

COPY --from=frontend /src/volumes/frontend/dist/default/browser/ /src/apps/default/static/

ENTRYPOINT ["gunicorn", "-w", "3", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "entrypoint:app"]
