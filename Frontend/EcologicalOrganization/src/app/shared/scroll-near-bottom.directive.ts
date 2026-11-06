import { Directive, EventEmitter, HostListener, Output } from '@angular/core';

const NEAR_BOTTOM_PX = 160;

@Directive({ selector: '[appScrollNearBottom]' })
export class ScrollNearBottomDirective {
  @Output() appScrollNearBottom = new EventEmitter<void>();

  @HostListener('scroll', ['$event.target'])
  emitIfNearBottom(element: HTMLElement): void {
    if (element.scrollTop + element.clientHeight >= element.scrollHeight - NEAR_BOTTOM_PX) {
      this.appScrollNearBottom.emit();
    }
  }
}
