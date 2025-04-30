// Encode the data and signing key as Uint8Array
const encoder = new TextEncoder();

// Webhook Goes Here
const data = {"id":31130332,"txid":"0x364435665b462be24a8d04028affa589d33d4c6bcfb36d51e2773ed916555963","raw":null,"walletid":7790,"type":"internal","fee":"0.00315329","effectivechange":"10.10000000","runningbalance":null,"timestamp":"2025-04-23T06:22:34.000Z","externaladdress":"0x2484e85405abbe4e2c9b839c5db934a1d11a75ae","block":null,"coin":"USDC","effectivechangeusd":"10.10000","wallet":{"id":7790,"name":"Red Envelope Holdings deposit POLYGON","type":"mpc","config":"2of2","balance":"9.50116452","address":"0xeF9C64c0978cd0AEF220B033f52939FBa2C144DD","chain":"POLYGON","subtype":"deposit","coin":"MATIC","orgid":1021,"parentchain":"EVM","isArchived":0,"balanceUSD":"0.00000000","orgWebhook":"https://liminal-webhook.redenvelope.dev"},"tokenContractAddress":"0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359","sequenceId":"","explorerLink":"https://polygonscan.com/tx/0x364435665b462be24a8d04028affa589d33d4c6bcfb36d51e2773ed916555963","inputs":[{"address":"0x2484e85405abbe4e2c9b839c5db934a1d11a75ae","amount":"0.00000000","isMine":true,"wallet":{"id":7789,"name":"Red Envelope Holdings withdrawal POLYGON","type":"mpc","config":"2of2","status":1,"balance":"13.13415061","balanceusd":"0.00000000","raw":null,"issynced":true,"walletpath":"m/44/60/1/1021/0/0/0","walletidentifier":"0x2484e85405aBbe4e2c9b839c5dB934A1d11A75AE","chain":"POLYGON","subtype":"hot","coin":"MATIC","orgid":1021,"parentchain":"EVM","canInitiatorSign":1,"suspendedStatus":0,"suspendedRemark":null,"isArchived":false,"teamId":null,"version":1,"account":null}}],"outputs":[{"address":"0x2746d3ed1d78420bb5523f7c78d93900f4e6224b","amount":"10.10000000","isMine":true,"wallet":{"id":7790,"name":"Red Envelope Holdings deposit POLYGON","type":"mpc","config":"2of2","status":1,"balance":"9.50116452","balanceusd":"0.00000000","raw":null,"issynced":true,"walletpath":"m/44/60/0/1021/0/0/0","walletidentifier":"0xeF9C64c0978cd0AEF220B033f52939FBa2C144DD","chain":"POLYGON","subtype":"deposit","coin":"MATIC","orgid":1021,"parentchain":"EVM","canInitiatorSign":1,"suspendedStatus":0,"suspendedRemark":null,"isArchived":false,"teamId":null,"version":1,"account":null}}],"blockConfirmation":null}
// Liminal Signing Key Goes Here
const liminalSigningKey = "f84fb77d-7ebf-790e-e28d-2466a10a0251";

const encodedData = encoder.encode(JSON.stringify(data));
const encodedKey = encoder.encode(liminalSigningKey);
(async () => {
	// Import the signing key to the crypto subsystem
	const cryptoKey = await crypto.subtle.importKey(
		"raw", // format
		encodedKey, // keyData
		{ name: "HMAC", hash: { name: "SHA-256" } }, // algorithm
		false, // extractable
		["sign"], // keyUsages
	);

	// Sign the data using the crypto key
	const signatureArrayBuffer = await crypto.subtle.sign(
		"HMAC",
		cryptoKey,
		encodedData,
	);

	// Convert the signature (ArrayBuffer) to a hex string
	const signature = Array.from(new Uint8Array(signatureArrayBuffer))
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");

	console.log(signature);
})();