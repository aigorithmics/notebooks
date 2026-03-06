import { UrlItem, ChipDescriptor } from 'kubeflow-aigo';

export interface VolumesGroup {
  name: string;
  array?: (UrlItem | ChipDescriptor)[];
  info?: string;
  url?: string;
}
