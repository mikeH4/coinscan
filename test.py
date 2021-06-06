from core.Token.ViewableToken import ViewableToken

x = ViewableToken.search("l")
for i in x:
    print(i.dict())