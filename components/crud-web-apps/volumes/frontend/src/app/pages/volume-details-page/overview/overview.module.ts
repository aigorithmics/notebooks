import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OverviewComponent } from './overview.component';
import { ContentListItemModule, KubeflowModule } from 'kubeflow-aigo';
import { LinkGroupsTableModule } from './link-groups-table/link-groups-table.module';

@NgModule({
  declarations: [OverviewComponent],
  imports: [
    CommonModule,
    KubeflowModule,
    ContentListItemModule,
    LinkGroupsTableModule,
  ],
  exports: [OverviewComponent],
})
export class OverviewModule {}
