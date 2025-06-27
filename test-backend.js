// Test script to verify ML backend connection
const BACKEND_URL = 'https://chef-gpt-c4sc.onrender.com';

async function testBackend() {
  console.log('🧪 Testing ML Backend Connection...');
  console.log(`📍 Backend URL: ${BACKEND_URL}`);
  console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);

  try {
    // Test health endpoint
    console.log('\n1. Testing health endpoint...');
    const healthResponse = await fetch(`${BACKEND_URL}/health`);
    const healthData = await healthResponse.json();
    console.log('✅ Health check:', healthData);

    // Test flyer dinner endpoint
    console.log('\n2. Testing flyer dinner endpoint...');
    const flyerResponse = await fetch(`${BACKEND_URL}/flyer_dinner`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ banner: 'no_frills' }),
    });

    if (flyerResponse.ok) {
      const flyerData = await flyerResponse.json();
      console.log('✅ Flyer dinner test:', flyerData);
    } else {
      console.log('❌ Flyer dinner test failed:', flyerResponse.status);
    }

    console.log('\n🎉 Backend connection test completed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run the test
testBackend();
