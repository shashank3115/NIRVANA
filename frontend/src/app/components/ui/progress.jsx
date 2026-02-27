import * as ProgressPrimitive from '@radix-ui/react-progress';
import { cn } from './utils';

export function Progress({ className, value = 0, ...props }) {
  return (
    <ProgressPrimitive.Root className={cn('bg-primary/20 relative h-2 w-full overflow-hidden rounded-full', className)} {...props}>
      <ProgressPrimitive.Indicator
        className="bg-primary h-full w-full flex-1 transition-all"
        style={{ transform: `translateX(-${100 - value}%)` }}
      />
    </ProgressPrimitive.Root>
  );
}
