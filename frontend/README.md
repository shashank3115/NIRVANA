# EnerScopeAI Frontend

Vite + React frontend for EnerScopeAI multi-renewable analysis.

## Scripts

- `npm run dev` — start local dev server
- `npm run lint` — run ESLint
- `npm run build` — production build
- `npm run preview` — preview production build

## Environment

- `VITE_API_URL` (optional)
	- Defaults to `http://localhost:8000`
	- Used by `src/services/apiService.js`

## Current Structure

```
src/
	app/
		AppRouter.jsx
		routes.jsx
		components/
			LocationMap.jsx
			ui/
				badge.jsx
				button.jsx
				card.jsx
				input.jsx
				progress.jsx
				tabs.jsx
				utils.js
		pages/
			Home.jsx
			Results.jsx
			About.jsx
			NotFound.jsx
			Root.jsx
	services/
		apiService.js
	styles/
		index.css
		tailwind.css
		theme.css
	App.jsx
	main.jsx
```

## Styling

- Tailwind CSS v4 via `@tailwindcss/vite`
- Theme tokens in `src/styles/theme.css`
- Global style imports in `src/styles/index.css`

## Routing Flow

- `/` → Home (location + params input)
- `/results` → runs multi-renewable analysis and renders recommendation UI
- `/about` → overview page
- `*` → Not Found
