# Engineering portfolio

The standalone site is deployed through GitHub Pages using `.github/workflows/portfolio-pages.yml`. It uses static HTML, CSS, JavaScript, repository-owned SVGs, and JSON. No package install, analytics, credentials, or production API access.

## Activate GitHub Pages
1. Open [Settings → Pages](https://github.com/navidalvand/navidalvand/settings/pages).
2. Under Build and deployment, select **GitHub Actions** as the source.
3. Open [Actions](https://github.com/navidalvand/navidalvand/actions), select **Deploy engineering portfolio**, and choose **Run workflow** on main.
4. After a successful deployment, open https://navidalvand.github.io/navidalvand/.

## Local preview
From repository root:
```sh
mkdir -p dist
cp -r site/. dist/
cp -r assets resume dist/
python3 scripts/verify_portfolio.py dist
python3 -m http.server 8000 --directory dist
```
Visit http://localhost:8000.

The case studies are local simulations with synthetic data; they are not production integrations or claims of performance. Public commit metrics are based on author-matched default-branch commits across public owned repositories and exclude private contributions, PRs and issues. Both activity visualizations use the same JSON snapshot.

The profile statistics workflow updates charts weekly. The Pages workflow runs after successful statistics refreshes and on main pushes. GitHub Pages must be enabled at repository level for deployment.
