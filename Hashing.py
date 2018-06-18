#!/usr/local/bin/python3


import hmac

def get_hash(k):
    message = input("Enter your message: ")
    hash = hmac.new(k.encode(), msg=message.encode(), digestmod='sha256')
    hash_ = hash.hexdigest()
    #print("\"" + message + "\" hashes to: " + hash_)
    return message, hash_

def get_hash_(message, k):
    hash = hmac.new(k.encode(), msg=message.encode(), digestmod='sha256')
    hash_ = hash.hexdigest()
    #print("\"" + message + "\" hashes to: " + hash_)
    return hash_

def check_hash(message, hash, key):
    hash_ = get_hash_(message, key)
    if hash_ == hash:
        return("Hashes Match")
    else:
        return("Hashes Do Not Match")



if __name__ == "__main__":
    k = input("Enter key: ")
    mess, h = get_hash()
    check_hash(mess, h, k)
    #Check that check_hash works for non-matching hashes
    mess_ = input("Enter changed message: ")
    check_hash(mess_, hash, k)
