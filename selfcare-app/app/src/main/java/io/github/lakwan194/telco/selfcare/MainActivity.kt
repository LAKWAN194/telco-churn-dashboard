package io.github.lakwan194.telco.selfcare

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import io.github.lakwan194.telco.selfcare.ui.theme.SelfCareTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            SelfCareTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { padding ->
                    HomeScreen(Modifier.padding(padding))
                }
            }
        }
    }
}

/** A placeholder home screen listing what the app will do. Design the real ones in week 4. */
@Composable
fun HomeScreen(modifier: Modifier = Modifier) {
    val features = listOf(
        R.string.feature_balance,
        R.string.feature_bundles,
        R.string.feature_offers,
        R.string.feature_offline,
    )
    Column(modifier = modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineMedium)
        Text(stringResource(R.string.home_intro), style = MaterialTheme.typography.bodyLarge)
        features.forEach { label -> ListItem(headlineContent = { Text(stringResource(label)) }) }
    }
}

@Preview(showBackground = true)
@Composable
private fun HomeScreenPreview() {
    SelfCareTheme { HomeScreen() }
}
