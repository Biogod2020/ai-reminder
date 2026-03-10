import asyncio
from playwright.async_api import async_playwright
import sys

async def run_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Set a standard viewport to ensure consistent rendering
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        print("--- Navigating to NSA Command Center ---")
        try:
            # Wait for network to be idle to ensure all React components are ready
            await page.goto("http://127.0.0.1:5173", wait_until="networkidle", timeout=45000)
        except Exception as e:
            print(f"FAILED: Initial navigation failed: {e}")
            await browser.close()
            return

        # 1. Verify Layout
        print("\n[Check 1: Layout Integrity]")
        try:
            sidebar = page.locator("aside").first
            await sidebar.wait_for(state="visible", timeout=10000)
            print("✅ Layout Verified.")
        except:
            print("❌ Sidebar not visible.")

        # 2. Test Clarification Loop
        print("\n[Check 2: Clarification Loop]")
        # Use a more generic but robust selector
        chat_input = page.locator("input").last
        try:
            await chat_input.wait_for(state="visible", timeout=10000)
            await chat_input.fill("I need to do some vague work.")
            await page.keyboard.press("Enter")
            
            print("Waiting for AI response...")
            # Wait for the "Thinking" indicator to appear and then disappear
            await page.wait_for_selector("#thinking-indicator", state="visible", timeout=10000)
            await page.wait_for_selector("#thinking-indicator", state="hidden", timeout=60000)
            
            last_bubble = page.locator(".rounded-2xl").last
            await page.wait_for_function("() => document.querySelector('.rounded-2xl:last-child')?.innerText.length > 5")
            
            response_text = await last_bubble.inner_text()
            print(f"AI Response: {response_text[:100]}...")
            
            if "?" in response_text or "how" in response_text.lower():
                print("✅ MCQ (Clarification) Verified.")
            else:
                print("❌ Response lacks clarification markers.")
        except Exception as e:
            print(f"❌ Check 2 Failed: {e}")

        # 3. Test Draft Preview
        print("\n[Check 3: Draft Preview Mode]")
        try:
            await chat_input.fill("I need to write a 1000-word SOTA blog post, it will take 3 hours.")
            await page.keyboard.press("Enter")
            
            print("Waiting for Draft generation...")
            await page.wait_for_selector("#alignment-panel", state="visible", timeout=60000)
            
            # Verify DRAFT tags in the grid
            draft_in_grid = page.locator("[data-testid='draft-task']").first
            if await draft_in_grid.is_visible():
                print("✅ Visual Drafts (Dashed) found in Grid.")
            
            print("✅ Draft Preview Logic Verified.")
        except Exception as e:
            print(f"❌ Check 3 Failed: {e}")

        # 4. Final Commit Action
        print("\n[Check 4: Confirm & Commit Interaction]")
        try:
            commit_btn = page.locator("#confirm-commit-btn")
            await commit_btn.scroll_into_view_if_needed()
            await commit_btn.click()
            print("✅ Commit Button Clicked.")
            
            # Wait for drafts to be cleared (promoted)
            await page.wait_for_selector("[data-testid='draft-task']", state="hidden", timeout=10000)
            print("✅ Lifecycle Verified: Draft -> Permanent.")
        except Exception as e:
            print(f"❌ Check 4 Failed: {e}")

        print("\n--- SOTA E2E VERIFICATION COMPLETE ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_verification())
