import { test, expect } from '@playwright/test';

const URL = 'http://159.89.231.16:3000';
const EMAIL = 'xio@email.com';
const PASSWORD = 'password';

const DOCTOR_NAME = `Dr. Test ${Date.now()}`;
const HOSPITAL_NAME = `Test Hospital ${Date.now()}`;
const DIAGNOSTIC_NAME = `Test Lab ${Date.now()}`;

async function login(page) {
  await page.goto(`${URL}/auth`);
  await page.locator('input').nth(0).waitFor();
  await page.locator('input').nth(0).fill(EMAIL);
  await page.locator('input').nth(1).fill(PASSWORD);
  await page.locator('form').getByRole('button', { name: 'Sign In' }).click();
  await page.waitForTimeout(3000);
}


async function selectDropdown(page, triggerText, optionIndex = 1) {
  await page.locator('[role="combobox"]').filter({ hasText: triggerText }).click();
  await page.waitForTimeout(500);
  // pick the option by index from the dropdown list
  await page.locator('[role="option"]').nth(optionIndex).click();
  await page.waitForTimeout(300);
}

test('Add new doctor with multiple hospitals and a profile picture', async ({ page }) => {
  await login(page);
  await page.goto(`${URL}/add-provider`);
  await page.getByRole('tab', { name: 'Doctor' }).waitFor();
  await page.getByRole('tab', { name: 'Doctor' }).click();
  await page.waitForTimeout(1000);

  await page.getByPlaceholder('Dr. John Smith').fill(DOCTOR_NAME);

  await selectDropdown(page, 'Select gender');
  await selectDropdown(page, 'Select city');
  await page.locator('#doctor-department').selectOption({ index: 1 });

  await page.getByPlaceholder('e.g., Cardiology, Neurology').fill('Cardiology, Neurology');
  await page.getByPlaceholder('e.g., MBBS, MD, FACC').fill('MBBS, MD');
  await page.getByPlaceholder('https://example.com/photo.jpg')
    .fill('https://randomuser.me/api/portraits/men/42.jpg');

  const checkboxes = page.locator('input[type="checkbox"]');
  await checkboxes.nth(0).check();
  await checkboxes.nth(1).check();
  await expect(page.getByText(/2 selected/i)).toBeVisible();

  await page.getByRole('button', { name: 'Submit Doctor' }).click();
  await expect(page.getByText(/success|submitted|created|added/i))
    .toBeVisible({ timeout: 10000 });
});

test('Add new hospital', async ({ page }) => {
  await login(page);
  await page.goto(`${URL}/add-provider`);
  await page.getByRole('tab', { name: 'Hospital' }).waitFor();
  await page.getByRole('tab', { name: 'Hospital' }).click();
  await page.waitForTimeout(1000);

  await page.getByPlaceholder('City General Hospital').fill(HOSPITAL_NAME);

  await selectDropdown(page, 'Select city');

  await page.getByPlaceholder('Full hospital address').fill('123 Test Street, Dhaka');
  await page.getByPlaceholder('+1 234 567 8900').fill('+1234567890');
  await page.getByPlaceholder('https://hospital.com').fill('https://testhospital.com');
  await page.getByPlaceholder('https://example.com/photo.jpg')
    .fill('https://randomuser.me/api/portraits/men/42.jpg');

  await page.getByRole('button', { name: 'Submit Hospital' }).click();
  await expect(page.getByText(/success|submitted|created|added/i))
    .toBeVisible({ timeout: 10000 });
});

test('Add new diagnostic center', async ({ page }) => {
  await login(page);
  await page.goto(`${URL}/add-provider`);
  await page.getByRole('tab', { name: 'Diagnostic Center' }).waitFor();
  await page.getByRole('tab', { name: 'Diagnostic Center' }).click();
  await page.waitForTimeout(1000);

  await page.getByPlaceholder('City Lab Services').fill(DIAGNOSTIC_NAME);

  await selectDropdown(page, 'Select city');

  await page.getByPlaceholder('Full center address').fill('456 Lab Road, Dhaka');
  await page.getByPlaceholder('+1 234 567 8900').fill('+1234567890');
  await page.getByPlaceholder('https://lab.com').fill('https://testlab.com');
  await page.getByPlaceholder('https://example.com/photo.jp')
    .fill('https://randomuser.me/api/portraits/men/42.jpg');
  await page.getByPlaceholder('https://maps.google.com/')
    .fill('https://maps.google.com/?q=Dhaka');

  await page.getByRole('button', { name: 'Submit Diagnostic Center' }).click();
  await expect(page.getByText(/success|submitted|created|added/i))
    .toBeVisible({ timeout: 10000 });
});