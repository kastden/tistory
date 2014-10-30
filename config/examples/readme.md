# Configuration file examples  

There are two files for Tistory, one is for the actual access token when using the API, and the other is for generating an access token with the OAuth2 helper in the tistory module.

#### tistory_credentials.json
The details in "client" needs to match the ones specified in your app at the [Tistory Developer Dashboard](http://www.tistory.com/guide/api/manage/register).  
The details in "cookies" needs to come from a valid non-expired session.  
The OAuth helper will authorize the app on behalf of the user (you), and then request an access token.

	{
	"client" : {
		"client_id" : "",
		"client_secret" : "",
		"callback" : ""
	},
	"cookies" : {
		"TSSESSION" : ""
	}
	}

#### tistory_access_token.json
	{
	"access_token" : ""
	}
