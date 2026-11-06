import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ScrollNearBottomDirective } from './scroll-near-bottom.directive';
import { SearchBoxComponent } from './search-box/search-box.component';

@NgModule({
  declarations: [SearchBoxComponent, ScrollNearBottomDirective],
  imports: [CommonModule, FormsModule],
  exports: [SearchBoxComponent, ScrollNearBottomDirective],
})
export class SharedModule {}
