import { test, expect } from '@playwright/test';

test('allows submitting a URL and viewing analysis results', async ({ page }) => {
  await page.goto('/');
  await page.fill('#url-input', 'https://example.com/pricing');
  await page.click('button[type="submit"]');

  await expect(page.getByTestId('analysis-summary')).toContainText(
    'example.com/pricing'
  );
  await expect(page.getByTestId('analysis-steps').locator('li')).toHaveCount(3);
});

test('shows actionable recommendations alongside the steps', async ({ page }) => {
  await page.goto('/');
  await page.fill('#url-input', 'https://example.com/signup');
  await page.click('button[type="submit"]');

  const recommendations = page.getByTestId('analysis-recommendations');
  await expect(recommendations.locator('li')).toHaveCount(2);
  await expect(recommendations).toContainText('testimonials');
});

test('renders embed view with query parameter URL', async ({ page }) => {
  await page.goto('/embed.html?url=https%3A%2F%2Fexample.com%2Fpromo');

  await expect(page.getByTestId('embed-summary')).toContainText('example.com/promo');
  await expect(page.getByTestId('embed-steps').locator('li')).toHaveCount(3);
});
