var dbPromise = idb.open('uno-db', 2, function(upgradeDb) {
  upgradeDb.createObjectStore('uno',{keyPath:'pk'});
 });


 fetch('http://127.0.0.1:9000/getdata').then(function(response){
  return response.json();
 }).then(function(jsondata){
  dbPromise.then(function(db){
   var tx = db.transaction('uno', 'readwrite');
     var feedsStore = tx.objectStore('uno');
     for(var key in jsondata){
      if (jsondata.hasOwnProperty(key)) {
        feedsStore.put(jsondata[key]); 
      }
     }
  });
 });

 var post="";
	dbPromise.then(function(db){
		var tx = db.transaction('uno', 'readonly');
  		var feedsStore = tx.objectStore('uno');
  		return feedsStore.openCursor();
	}).then(function logItems(cursor) {
		  if (!cursor) {
		  	document.getElementById('offlinedata').innerHTML=post;
		    return;
		  }
		  for (var field in cursor.value) {
		    	if(field=='fields'){
		    		feedsData=cursor.value[field];
		    		for(var key in feedsData){

              if(key =='title'){
		    				var title = '<h3>'+feedsData[key]+'</h3>';
		    			}

		    			if(key =='subtitle'){
		    				var subtitle = '<h3>'+feedsData[key]+'</h3>';
		    			}
		    			if(key =='author'){
		    				var author = feedsData[key];
		    			}
		    			if(key == 'body'){
		    				var body = '<p>'+feedsData[key]+'</p>';
		    			}	
		    		}
		    		post=post+'<br>'+title+'<br>'+subtitle+'<br>'+author+'<br>'+body+'<br>';
		    	}
		    }
		  return cursor.continue().then(logItems);
    });
    
