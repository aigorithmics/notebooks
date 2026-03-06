import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { YamlComponent } from './yaml.component';
import { EditorModule } from 'kubeflow-aigo';

@NgModule({
  declarations: [YamlComponent],
  imports: [CommonModule, EditorModule],
  exports: [YamlComponent],
})
export class YamlModule {}
