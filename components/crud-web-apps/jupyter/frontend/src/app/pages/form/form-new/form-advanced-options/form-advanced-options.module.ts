import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormModule as KfFormModule } from 'kubeflow-aigo';
import { FormAdvancedOptionsComponent } from './form-advanced-options.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

@NgModule({
  declarations: [FormAdvancedOptionsComponent],
  imports: [CommonModule, KfFormModule, MatSlideToggleModule],
  exports: [FormAdvancedOptionsComponent],
})
export class FormAdvancedOptionsModule {}
