package io.github.lakwan194.telco.selfcare

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.test.ext.junit.runners.AndroidJUnit4
import io.github.lakwan194.telco.selfcare.ui.theme.SelfCareTheme
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Runs on a device or emulator: `./gradlew connectedDebugAndroidTest`. */
@RunWith(AndroidJUnit4::class)
class HomeScreenTest {

    @get:Rule
    val compose = createComposeRule()

    @Test
    fun showsThePlannedFeatures() {
        compose.setContent { SelfCareTheme { HomeScreen() } }
        compose.onNodeWithText("Offer inbox").assertIsDisplayed()
        compose.onNodeWithText("Works offline").assertIsDisplayed()
    }
}
