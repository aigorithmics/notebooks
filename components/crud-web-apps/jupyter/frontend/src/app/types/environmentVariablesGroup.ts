import { PodDefault } from 'src/app/types';
import { VariablesGroup } from 'kubeflow-aigo';

export interface EnvironmentVariablesGroup extends VariablesGroup {
  configuration?: PodDefault;
}
