import { cn } from './utils';

export function Card({ className, ...props }) {
  return <div className={cn('bg-card text-card-foreground flex flex-col rounded-xl border', className)} {...props} />;
}

export function CardHeader({ className, ...props }) {
  return <div className={cn('px-6 pt-6', className)} {...props} />;
}

export function CardTitle({ className, ...props }) {
  return <h4 className={cn('leading-none font-semibold', className)} {...props} />;
}

export function CardContent({ className, ...props }) {
  return <div className={cn('px-6 pb-6', className)} {...props} />;
}
