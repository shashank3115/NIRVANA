import { cn } from './utils';

export function Input({ className, type = 'text', ...props }) {
  return (
    <input
      type={type}
      className={cn(
        'placeholder:text-muted-foreground border-input flex h-9 w-full rounded-md border px-3 py-1 text-base bg-input-background transition-[color,box-shadow] outline-none md:text-sm focus-visible:ring-[3px] focus-visible:ring-ring/50',
        className,
      )}
      {...props}
    />
  );
}
