import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { NamespaceSelectComponent } from './namespace-select.component';
import { SnackBarModule } from '../snack-bar/snack-bar.module';

@NgModule({
  declarations: [NamespaceSelectComponent],
  exports: [NamespaceSelectComponent],
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatSelectModule,
    SnackBarModule,
  ],
})
export class NamespaceSelectModule {}
