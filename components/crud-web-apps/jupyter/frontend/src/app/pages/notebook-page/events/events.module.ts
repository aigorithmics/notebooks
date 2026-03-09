import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EventsComponent } from './events.component';
import { KubeflowModule } from 'kubeflow-aigo';

@NgModule({
  declarations: [EventsComponent],
  imports: [CommonModule, KubeflowModule],
  exports: [EventsComponent],
})
export class EventsModule {}
