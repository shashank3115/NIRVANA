import * as TabsPrimitive from '@radix-ui/react-tabs';
import { cn } from './utils';

export function Tabs({ className, ...props }) {
  return <TabsPrimitive.Root className={cn('flex flex-col gap-2', className)} {...props} />;
}

export function TabsList({ className, ...props }) {
  return (
    <TabsPrimitive.List
      className={cn('bg-muted text-muted-foreground inline-flex h-9 w-fit items-center justify-center rounded-xl p-[3px] flex', className)}
      {...props}
    />
  );
}

export function TabsTrigger({ className, ...props }) {
  return (
    <TabsPrimitive.Trigger
      className={cn('data-[state=active]:bg-card text-foreground inline-flex h-[calc(100%-1px)] flex-1 items-center justify-center rounded-xl px-2 py-1 text-sm font-medium transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:ring-ring/50', className)}
      {...props}
    />
  );
}

export function TabsContent({ className, ...props }) {
  return <TabsPrimitive.Content className={cn('flex-1 outline-none', className)} {...props} />;
}
