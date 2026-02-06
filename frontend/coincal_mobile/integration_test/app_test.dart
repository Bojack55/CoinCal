import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:coincal_mobile/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('E2E User Journey Simulation', () {
    testWidgets('Calculate Nutrition flow', (tester) async {
      // 1. Load the app
      app.main();
      await tester.pumpAndSettle();

      // Robust Login Step using Keys
      final loginBtn = find.byKey(const Key('login_btn'));
      if (loginBtn.evaluate().isNotEmpty) {
        await tester.enterText(
          find.byKey(const Key('login_email')),
          'testuser',
        );
        await tester.enterText(
          find.byKey(const Key('login_password')),
          'password123',
        );
        await tester.tap(loginBtn);
        // Wait longer for session setup and dashboard load
        await tester.pumpAndSettle();
        await tester.pump(const Duration(seconds: 3));
      }

      // 2. Navigate to Nutrition Calculator Screen via Bottom Bar Key
      final calcIcon = find.byKey(const Key('nav_calc'));
      expect(calcIcon, findsOneWidget);

      await tester.pumpAndSettle();
      await tester.tap(calcIcon);
      await tester.pumpAndSettle();

      // 3. Select a Meal from the Dropdown
      final dropdown = find.byKey(const Key('meal_dropdown'));
      expect(dropdown, findsOneWidget);

      await tester.pumpAndSettle();
      await tester.tap(dropdown);
      await tester.pumpAndSettle();

      // Tap 'Koshary' or the first item found using textContaining
      final kosharyItem = find.textContaining('Koshary').last;
      await tester.tap(kosharyItem);
      await tester.pumpAndSettle();

      // 4. Enter Weight (300g)
      final weightInput = find.byKey(const Key('weight_input'));
      expect(weightInput, findsOneWidget);

      await tester.enterText(weightInput, '300');
      await tester.pumpAndSettle();

      // 5. Tap the Calculate Button
      final calcBtn = find.byKey(const Key('calculate_btn'));
      expect(calcBtn, findsOneWidget);

      await tester.pumpAndSettle();
      await tester.tap(calcBtn);

      // Wait for API response and animations
      await tester.pump(const Duration(seconds: 4));
      await tester.pumpAndSettle();

      // 6. Assertion: Verify Result
      final resultDisplay = find.byKey(const Key('result_display'));
      expect(resultDisplay, findsOneWidget);

      final calorieText = find.textContaining('calories');
      expect(calorieText, findsOneWidget);
    });

    group('Navigation Verification', () {
      testWidgets('Tab switching stability', (tester) async {
        app.main();
        await tester.pumpAndSettle();

        // Ensure we are logged in
        final loginBtn = find.byKey(const Key('login_btn'));
        if (loginBtn.evaluate().isNotEmpty) {
          await tester.enterText(
            find.byKey(const Key('login_email')),
            'testuser',
          );
          await tester.enterText(
            find.byKey(const Key('login_password')),
            'password123',
          );
          await tester.tap(loginBtn);
          await tester.pumpAndSettle();
          await tester.pump(const Duration(seconds: 3));
        }

        // Tap 'Kitchen' tab via Key
        await tester.pumpAndSettle();
        await tester.tap(find.byKey(const Key('nav_kitchen')));
        await tester.pumpAndSettle();
        expect(find.textContaining('Recipe Studio'), findsWidgets);

        // Tap 'Profile' tab via Key
        await tester.pumpAndSettle();
        await tester.tap(find.byKey(const Key('nav_profile')));
        await tester.pumpAndSettle();
        expect(find.textContaining('Profile'), findsWidgets);

        // Return to Home
        await tester.pumpAndSettle();
        await tester.tap(find.byKey(const Key('nav_home')));
        await tester.pumpAndSettle();
      });
    });
  });
}
