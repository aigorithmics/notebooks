import { Injectable } from '@angular/core';
import { Observable, Subscription } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class PollerService {
  constructor() {}

  public exponential<T>(obs: Observable<T>): Observable<T> {
    return new Observable<T>(subscriber => {
      let period = 1;
      let currData: string | undefined;
      let timeoutId: ReturnType<typeof setTimeout> | null = null;
      let innerSub: Subscription | null = null;

      const poll = () => {
        innerSub = obs.subscribe({
          next: data => {
            const serialized = JSON.stringify(data);
            if (serialized !== currData) {
              // new data detected, reset period
              if (currData !== undefined) {
                period = 1;
              }
              currData = serialized;
              subscriber.next(data);
            }
            period = Math.min(period * 2, 8);
            timeoutId = setTimeout(poll, period * 1000);
          },
          error: () => {
            // On error, continue polling with backoff
            period = Math.min(period * 2, 8);
            timeoutId = setTimeout(poll, period * 1000);
          },
        });
      };

      // Start polling immediately
      poll();

      // Cleanup on unsubscribe
      return () => {
        if (timeoutId !== null) {
          clearTimeout(timeoutId);
        }
        if (innerSub !== null) {
          innerSub.unsubscribe();
        }
      };
    });
  }
}
