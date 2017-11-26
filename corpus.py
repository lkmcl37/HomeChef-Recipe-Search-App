import urllib2
import json
import traceback
data=list(range(1930000,1931000))

obj = open('data.json', 'wb')
out={}
key='p2ELF989mf4Se9T2V53SOcaUBTnM7y28'
for i in data:

    try:
        f = urllib2.urlopen('http://api2.bigoven.com/recipe/'+str(i)+'?api_key='+key)

        json_string = f.read()
        parse=json.loads(json_string)
        out[str(i)]=parse
        f.close()
        print i
    except:
        pass
        # traceback.print_exc()

json_d=json.dumps(out)
obj = open('data_sample.json', 'wb')
obj.write(json_d)
obj.close
