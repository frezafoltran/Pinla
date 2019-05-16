import math
import math
import json
from  app.helper_lyric_generator import phonetic_clean

def dist(word_1:str, word_2:str, alliteration = False):

    # get phonetic and metaphone of word to be compared
    all_phonetics = get_all_phonetic_array()
    bool_1 = True
    bool_2 = True
    try:
        info_1 = all_phonetics[word_1]
    except KeyError:
        bool_1 = False

    try:
        info_2 = all_phonetics[word_2]
    except KeyError:
        bool_2 = False

    # neither word is in database
    if (not bool_1) and (not bool_2):
        return -3
    # word 1 not in database
    elif not bool_1:
        return -1
    # word 2 not in database
    elif not bool_2:
        return -2

    phon_dist = phonetic_dist(info_1[0], info_2[0], alliteration)
    meta_dist = metaphone_dist(info_1[1], info_2[1], alliteration)
    total_dist = adjust_range(phon_dist, meta_dist)

    return total_dist

def phonetic_dist(p1, p2, alliteration=False, tune=[4, 1], ):
    """This method gives the rhyme distance between two given words, based on
    edit distance"""

    # formats input to distance functions
    p1 = phonetic_clean(str(p1))
    p2 = phonetic_clean(str(p2))
    p1 = str(p1).replace("\'", "")
    p2 = str(p2).replace("\'", "")


    # if alliteration is set to True, compare initial overlapping syllables
    if alliteration:
        return alliteration_dist(p1, p2, tune)

    # if alliteration is set to False, compare last overlapping syllables
    else:
        return rhyme_dist(p1, p2, tune)

def alliteration_dist(p1, p2, tune=[4, 1], dist=0):
    """This function returns the phonetic distance between two words, while
    prioritizing alliteration rhyme (i.e. rhymes that occur in the beginning of
    word).The tune parameter is a list, where the first entry corresponds to
    the syllable size to be compared and the second corresponds to weight
    adjustments.
    """

    size = tune[0]
    weight = tune[1]

    # do we need the +1 here?
    if weight == 1 and len(p1) < size:
        dist = edit_dist(p1, p2[:len(p1)+1])

    elif weight == 1 and len(p2) < size:
        dist = edit_dist(p1[:len(p2)+1], p2)

    elif len(p1) >= size and len(p2) >= size:
        dist += edit_dist(p1[:size+1], p2[:size+1]) / weight

    else:
        return dist

    return alliteration_dist(p1[size+1:], p2[size+1:], [size, weight + 1], dist)

def rhyme_dist(p1, p2, tune=[4, 1], dist=0):
    """This function return the phonetic distance between two words, while
    prioraizing rhymes (i.e. rhymes that occur in the end of
    word).The tunning parameter is a list, where the first entry corresponds to
    the syllable size to be compared and the second corresponds to weight
    adjustments.
    """

    size = tune[0]
    weight = tune[1]

    if weight == 1 and len(p1) < size:
        dist = edit_dist(p1, p2[len(p2) - len(p1):])

    elif weight == 1 and len(p2) < size:
        dist = edit_dist(p1[len(p1) - len(p2):], p2)

    elif len(p1) >= size and len(p2) >= size:
        dist += edit_dist(p1[len(p1) - size:], p2[len(p2) - size:]) / weight

    else:
        return dist

    return rhyme_dist(p1[:-size], p2[:-size], [size, weight + 1], dist)


def memoize(func):
    """This method optimizes the runtime of edit_distance method by storing
    some of the values needed in the recursive calls"""

    mem = {}

    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in mem:
            mem[key] = func(*args, **kwargs)
        return mem[key]

    return memoizer


@memoize
def edit_dist(a, b):
    """This method implements the usual edit_distance algorithm."""
    if a == "":
        return len(b)
    if b == "":
        return len(a)
    if a[-1] == b[-1] and (a[-1] in ("a","e", "i", "o", "u") and b[-1] in ("a","e", "i", "o", "u")):
        cost = -1
    elif a[-1] == b[-1]:
        cost = 0
    else:
        cost = 1

    res = min([edit_dist(a[:-1], b) + 1,
               edit_dist(a, b[:-1]) + 1,
               edit_dist(a[:-1], b[:-1]) + cost])

    return res

def metaphone_dist(met1:str, met2:str, alliteration=False):

    if len(met1)<len(met2):
        small = met1
        large = met2
    else:
        small = met2
        large = met1

    if alliteration:
        #Ensures that focus is given to first letters
        if len(small) > 3:
            split = max(math.floor(len(small) / 2),3)+1
            return edit_dist(large[:split], small[:split])*split + edit_dist(large[split:], small[split:])
        else:
            return edit_dist(large[:len(large)-len(small)+2], small) * 3

    else:
        #Ensures that focus is given to last letters
        if len(small) > 3:
            split = max(math.floor(len(small) / 2),3)
            return edit_dist(large[split:], small[split:])*split + edit_dist(large[:split], small[:split])
        else:
            return edit_dist(large[len(large)-len(small):], small) * 3

def adjust_range(d1, d2):
    # Since we are not interested in rhymes that are too weak, we limit our analysis to the cases that yield
    # distances smaller than 10. i.e. focus on range -3,10 for safe margin. This function returns a value between 0 and 1
    #d1 is phon_dist and d2 is meta_dist

    total_dist = d1 + d2 * 0.5

    if total_dist >= 10:
        return 1

    elif total_dist <= -3:
        return 0

    else:
        return (total_dist + 3)/13


def get_all_phonetic_array():
    # I have this option set to true because I already saved it in JSON
    corpus = {
    "a": [
        "[ey,]",
        "A"
    ],
    "aa": [
        "[ah,ah]",
        "A"
    ],
    "aah": [
        "[ah]",
        "A"
    ],
    "abandon": [
        "[uh,ban,duhn]",
        "APNTN"
    ],
    "abandoned": [
        "[uh,ban,duhnd]",
        "APNTNT"
    ],
    "abc": [
        "[ey,bee,see]",
        "APK"
    ],
    "abdomen": [
        "[ab,duh,muhn]",
        "APTMN"
    ],
    "abel": [
        "[ey,buhl]",
        "APL"
    ],
    "abide": [
        "[uh,bahyd]",
        "APT"
    ],
    "ability": [
        "[uh,bil,i,tee]",
        "APLT"
    ],
    "able": [
        "[ey,buhl]",
        "APL"
    ],
    "aboard": [
        "[uh,bawrd]",
        "APRT"
    ],
    "abort": [
        "[uh,bawrt]",
        "APRT"
    ],
    "abortion": [
        "[uh,bawr,shuhn]",
        "APRXN"
    ],
    "abortions": [
        "[uh,bawr,shuhn,s]",
        "APRXNS"
    ],
    "about": [
        "[uh,bout]",
        "APT"
    ],
    "above": [
        "[uh,buhv]",
        "APF"
    ],
    "abracadabra": [
        "[ab,ruh,kuh,dab,ruh]",
        "APRKTPR"
    ],
    "abroad": [
        "[uh,brawd]",
        "APRT"
    ],
    "abs": [
        "[abz]",
        "APS"
    ],
    "absence": [
        "[ab,suhns]",
        "APSNS"
    ],
    "absent": [
        "[adjective]",
        "APSNT"
    ],
    "absolutely": [
        "[ab,suh,loot,lee]",
        "APSLTL"
    ],
    "absurd": [
        "[ab,surd]",
        "APSRT"
    ],
    "abundance": [
        "[uh,buhn,duhns]",
        "APNTNS"
    ],
    "abuse": [
        "[verbuh,byooz]",
        "APS"
    ],
    "abusers": [
        "[verbuh,byooz,rs]",
        "APSRS"
    ],
    "abusive": [
        "[uh,byoo,siv]",
        "APSF"
    ],
    "ac": [
        "[k,tn,m]",
        "AK"
    ],
    "academy": [
        "[uh,kad,uh,mee]",
        "AKTM"
    ],
    "accent": [
        "[nounak,sent]",
        "AKSNT"
    ],
    "accept": [
        "[ak,sept]",
        "AKSPT"
    ],
    "acceptance": [
        "[ak,sep,tuhns]",
        "AKSPTNS"
    ],
    "accepted": [
        "[ak,sep,tid]",
        "AKSPTT"
    ],
    "accepting": [
        "[ak,sep,ting]",
        "AKSPTNK"
    ],
    "access": [
        "[ak,ses]",
        "AKSS"
    ],
    "accident": [
        "[ak,si,duhnt]",
        "AKSTNT"
    ],
    "accidentally": [
        "[ak,si,den,tl,ly]",
        "AKSTNTL"
    ],
    "accidents": [
        "[ak,si,duhnt,s]",
        "AKSTNTS"
    ],
    "accolades": [
        "[ak,uh,leyd,s]",
        "AKLTS"
    ],
    "accomplish": [
        "[uh,kom,plish]",
        "AKMPLX"
    ],
    "accomplished": [
        "[uh,kom,plisht]",
        "AKMPLXT"
    ],
    "accord": [
        "[uh,kawrd]",
        "AKRT"
    ],
    "according": [
        "[uh,kawr,ding]",
        "AKRTNK"
    ],
    "accordingly": [
        "[uh,kawr,ding,lee]",
        "AKRTNKL"
    ],
    "accordion": [
        "[uh,kawr,dee,uhn]",
        "AKRTN"
    ],
    "account": [
        "[uh,kount]",
        "AKNT"
    ],
    "accountant": [
        "[uh,koun,tnt]",
        "AKNTNT"
    ],
    "accountants": [
        "[uh,koun,tnt,s]",
        "AKNTNTS"
    ],
    "accounts": [
        "[uh,kount,s]",
        "AKNTS"
    ],
    "accurate": [
        "[ak,yer,it]",
        "AKRT"
    ],
    "accused": [
        "[uh,kyoozd]",
        "AKST"
    ],
    "accustomed": [
        "[uh,kuhs,tuhmd]",
        "AKSTMT"
    ],
    "ace": [
        "[eys]",
        "AS"
    ],
    "aces": [
        "[eys,s]",
        "ASS"
    ],
    "ache": [
        "[eyk]",
        "AX"
    ],
    "achieve": [
        "[uh,cheev]",
        "AXF"
    ],
    "achievement": [
        "[uh,cheev,muhnt]",
        "AXFMNT"
    ],
    "achilles": [
        "[uh,kil,eez]",
        "AXLS"
    ],
    "aching": [
        "[ey,king]",
        "AXNK"
    ],
    "acid": [
        "[as,id]",
        "AST"
    ],
    "acknowledge": [
        "[ak,nol,ij]",
        "AKNLJ"
    ],
    "acne": [
        "[ak,nee]",
        "AKN"
    ],
    "acquainted": [
        "[uh,kweyn,tid]",
        "AKNTT"
    ],
    "acquire": [
        "[uh,kwahyuhr]",
        "AKR"
    ],
    "acre": [
        "[ey,ker]",
        "AKR"
    ],
    "acres": [
        "[ey,ker,s]",
        "AKRS"
    ],
    "acrobat": [
        "[ak,ruh,bat]",
        "AKRPT"
    ],
    "acrobats": [
        "[ak,ruh,bat,s]",
        "AKRPTS"
    ],
    "across": [
        "[uh,kraws]",
        "AKRS"
    ],
    "act": [
        "[akt]",
        "AKT"
    ],
    "acted": [
        "['akt', 'ed']",
        "AKTT"
    ],
    "acting": [
        "['ak', 'ting']",
        "AKTNK"
    ],
    "action": [
        "['ak', 'shuhn']",
        "AKXN"
    ],
    "actions": [
        "['ak', 'shuhn', 's']",
        "AKXNS"
    ],
    "activated": [
        "[ak,tuh,veyt,d]",
        "AKTFTT"
    ],
    "active": [
        "['ak', 'tiv']",
        "AKTF"
    ],
    "activist": [
        "['ak', 'tuh', 'vist']",
        "AKTFST"
    ],
    "activists": [
        "['ak', 'tuh', 'vist', 's']",
        "AKTFSTS"
    ],
    "activity": [
        "[ak,tiv,i,tee]",
        "AKTFT"
    ],
    "actor": [
        "[ak,ter]",
        "AKTR"
    ],
    "actors": [
        "['ak', 'ter', 's']",
        "AKTRS"
    ],
    "actress": [
        "['ak', 'tris']",
        "AKTRS"
    ],
    "actresses": [
        "[ak,tris,es]",
        "AKTRSS"
    ],
    "acts": [
        "[akt,s]",
        "AKTS"
    ],
    "actual": [
        "[ak,choo,uhl]",
        "AKTL"
    ],
    "actually": [
        "['ak', 'choo', 'uh', 'lee']",
        "AKTL"
    ],
    "ad": [
        "['ad']",
        "AT"
    ],
    "adage": [
        "[ad,ij]",
        "ATJ"
    ],
    "adam": [
        "['ad', 'uhmfor1']",
        "ATM"
    ],
    "adapt": [
        "['uh', 'dapt']",
        "ATPT"
    ],
    "add": [
        "['ad']",
        "AT"
    ],
    "added": [
        "['ad', 'ed']",
        "ATT"
    ],
    "adderall": [
        "['ad', 'uh', 'rawl']",
        "ATRL"
    ],
    "addict": [
        "['nounad', 'ikt']",
        "ATKT"
    ],
    "addicted": [
        "['uh', 'dik', 'tid']",
        "ATKTT"
    ],
    "addiction": [
        "['uh', 'dik', 'shuhn']",
        "ATKXN"
    ],
    "addictive": [
        "[uh,dik,tiv]",
        "ATKTF"
    ],
    "addicts": [
        "['nounad', 'ikt', 's']",
        "ATKTS"
    ],
    "adding": [
        "['ad', 'ing']",
        "ATNK"
    ],
    "additional": [
        "[uh,dish,uh,nl]",
        "ATXNL"
    ],
    "address": [
        "['nounuh', 'dres']",
        "ATRS"
    ],
    "addressing": [
        "['nounuh', 'dres', 'ing']",
        "ATRSNK"
    ],
    "adios": [
        "[ad,ee,ohs]",
        "ATS"
    ],
    "adjust": [
        "['uh', 'juhst']",
        "ATJST"
    ],
    "adjusting": [
        "[uh,juhst,ing]",
        "ATJSTNK"
    ],
    "admiration": [
        "[ad,muh,rey,shuhn]",
        "ATMRXN"
    ],
    "admire": [
        "['ad', 'mahyuhr']",
        "ATMR"
    ],
    "admired": [
        "[ad,mahyuhr,d]",
        "ATMRT"
    ],
    "admiring": [
        "['ad', 'mahyuhr', 'ing']",
        "ATMRNK"
    ],
    "admit": [
        "['ad', 'mit']",
        "ATMT"
    ],
    "admitted": [
        "[ad,mit,ted]",
        "ATMTT"
    ],
    "admitting": [
        "[ad,mit,ting]",
        "ATMTNK"
    ],
    "adolescence": [
        "[ad,l,es,uhns]",
        "ATLSNS"
    ],
    "adolescent": [
        "[ad,l,es,uhnt]",
        "ATLSNT"
    ],
    "adonis": [
        "[uh,don,is]",
        "ATNS"
    ],
    "adore": [
        "['uh', 'dawr']",
        "ATR"
    ],
    "adrenaline": [
        "['uh', 'dren', 'l', 'in']",
        "ATRNLN"
    ],
    "ads": [
        "[ad]",
        "ATS"
    ],
    "advance": [
        "['ad', 'vans']",
        "ATFNS"
    ],
    "advanced": [
        "[ad,vanst]",
        "ATFNST"
    ],
    "advances": [
        "[ad,vans,s]",
        "ATFNSS"
    ],
    "advantage": [
        "['ad', 'van', 'tij']",
        "ATFNTJ"
    ],
    "adventure": [
        "[ad,ven,cher]",
        "ATFNTR"
    ],
    "adversity": [
        "['ad', 'vur', 'si', 'tee']",
        "ATFRST"
    ],
    "advice": [
        "['ad', 'vahys']",
        "ATFS"
    ],
    "advil": [
        "['ad', 'vil']",
        "ATFL"
    ],
    "advise": [
        "['ad', 'vahyz']",
        "ATFS"
    ],
    "advised": [
        "[ad,vahyzd]",
        "ATFST"
    ],
    "aerosol": [
        "['air', 'uh', 'sawl']",
        "ARSL"
    ],
    "afar": [
        "['uh', 'fahr']",
        "AFR"
    ],
    "affair": [
        "[uh,fair]",
        "AFR"
    ],
    "affairs": [
        "[uh,fair,s]",
        "AFRS"
    ],
    "affect": [
        "[verbuh,fekt]",
        "AFKT"
    ],
    "affection": [
        "[uh,fek,shuhn]",
        "AFKXN"
    ],
    "affiliated": [
        "[uh,fil,ee,ey,tid]",
        "AFLTT"
    ],
    "afford": [
        "['uh', 'fawrd']",
        "AFRT"
    ],
    "affronted": [
        "[uh,fruhnt,ed]",
        "AFRNTT"
    ],
    "afghanistan": [
        "['af', 'gan', 'uh', 'stan']",
        "AFKNSTN"
    ],
    "afloat": [
        "[uh,floht]",
        "AFLT"
    ],
    "afraid": [
        "['uh', 'freyd']",
        "AFRT"
    ],
    "africa": [
        "['af', 'ri', 'kuh']",
        "AFRK"
    ],
    "african": [
        "['af', 'ri', 'kuhn']",
        "AFRKN"
    ],
    "africans": [
        "[af,ri,kuhn,s]",
        "AFRKNS"
    ],
    "afro": [
        "[af,roh]",
        "AFR"
    ],
    "afros": [
        "['af', 'roh', 's']",
        "AFRS"
    ],
    "after": [
        "['af', 'ter']",
        "AFTR"
    ],
    "afterlife": [
        "['af', 'ter', 'lahyf']",
        "AFTRLF"
    ],
    "aftermath": [
        "[af,ter,math]",
        "AFTRM0"
    ],
    "afternoon": [
        "['nounaf', 'ter', 'noon']",
        "AFTRNN"
    ],
    "afternoons": [
        "[af,ter,noonz]",
        "AFTRNNS"
    ],
    "again": [
        "['uh', 'gen']",
        "AKN"
    ],
    "against": [
        "['uh', 'genst']",
        "AKNST"
    ],
    "age": [
        "['eyj']",
        "AJ"
    ],
    "agenda": [
        "[uh,jen,duh]",
        "AJNT"
    ],
    "agent": [
        "['ey', 'juhnt']",
        "AJNT"
    ],
    "agents": [
        "[ey,juhnt,s]",
        "AJNTS"
    ],
    "ages": [
        "['eyj', 's']",
        "AJS"
    ],
    "aggravated": [
        "['ag', 'ruh', 'vey', 'tid']",
        "AKRFTT"
    ],
    "aggression": [
        "[uh,gresh,uhn]",
        "AKRSN"
    ],
    "aggressive": [
        "[uh,gres,iv]",
        "AKRSF"
    ],
    "agitated": [
        "['aj', 'i', 'tey', 'tid']",
        "AJTTT"
    ],
    "ago": [
        "['uh', 'goh']",
        "AK"
    ],
    "agony": [
        "[ag,uh,nee]",
        "AKN"
    ],
    "agree": [
        "['uh', 'gree']",
        "AKR"
    ],
    "agreed": [
        "[uh,greed]",
        "AKRT"
    ],
    "agreement": [
        "['uh', 'gree', 'muhnt']",
        "AKRMNT"
    ],
    "ah": [
        "['ah']",
        "A"
    ],
    "ahead": [
        "['uh', 'hed']",
        "AHT"
    ],
    "ahem": [
        "[pronouncedwithasmallscrapingsoundaccompaniedorfollowedbyanasal]",
        "AHM"
    ],
    "ai": [
        "[ah,ee]",
        "A"
    ],
    "aid": [
        "[eyd]",
        "AT"
    ],
    "aids": [
        "['eydz']",
        "ATS"
    ],
    "aim": [
        "['eym']",
        "AM"
    ],
    "aimed": [
        "[eym,ed]",
        "AMT"
    ],
    "aiming": [
        "['eym', 'ing']",
        "AMNK"
    ],
    "ain": [
        "['eyn']",
        "AN"
    ],
    "ain't": [
        "['eynt']",
        "ANNT"
    ],
    "air": [
        "['air']",
        "AR"
    ],
    "aired": [
        "['air', 'ed']",
        "ART"
    ],
    "airline": [
        "['air', 'lahyn']",
        "ARLN"
    ],
    "airplane": [
        "[air,pleyn]",
        "ARPLN"
    ],
    "airport": [
        "['air', 'pawrt']",
        "ARPRT"
    ],
    "airports": [
        "['air', 'pawrt', 's']",
        "ARPRTS"
    ],
    "airs": [
        "[air,s]",
        "ARS"
    ],
    "airwaves": [
        "[air,weyvz]",
        "ARFS"
    ],
    "aisle": [
        "['ahyl']",
        "AL"
    ],
    "ajax": [
        "[ey,jaks]",
        "AJKS"
    ],
    "al": [
        "['ahl']",
        "AL"
    ],
    "alabama": [
        "['al', 'uh', 'bam', 'uh']",
        "ALPM"
    ],
    "aladdin": [
        "['uh', 'lad', 'n']",
        "ALTN"
    ],
    "alarm": [
        "[uh,lahrm]",
        "ALRM"
    ],
    "alarms": [
        "['uh', 'lahrm', 's']",
        "ALRMS"
    ],
    "alaska": [
        "['uh', 'las', 'kuh']",
        "ALSK"
    ],
    "albino": [
        "['al', 'bahy', 'nohor']",
        "ALPN"
    ],
    "album": [
        "['al', 'buhm']",
        "ALPM"
    ],
    "album's": [
        "[al,buhm,'s]",
        "ALPMMS"
    ],
    "albums": [
        "['al', 'buhm', 's']",
        "ALPMS"
    ],
    "alcohol": [
        "['al', 'kuh', 'hawl']",
        "ALKHL"
    ],
    "alcoholic": [
        "['al', 'kuh', 'haw', 'lik']",
        "ALKHLK"
    ],
    "alcoholics": [
        "[al,kuh,haw,lik,s]",
        "ALKHLKS"
    ],
    "alert": [
        "['uh', 'lurt']",
        "ALRT"
    ],
    "alexander": [
        "['al', 'ig', 'zan', 'der']",
        "ALKSNTR"
    ],
    "alfred": [
        "[al,fred]",
        "ALFRT"
    ],
    "ali": [
        "['ah', 'lee']",
        "AL"
    ],
    "alias": [
        "['ey', 'lee', 'uhs']",
        "ALS"
    ],
    "alibis": [
        "[al,uh,bahy,s]",
        "ALPS"
    ],
    "alicia": [
        "['uh', 'lish', 'uh']",
        "ALS"
    ],
    "alien": [
        "['eyl', 'yuhn']",
        "ALN"
    ],
    "alienated": [
        "['eyl', 'yuh', 'neyt', 'd']",
        "ALNTT"
    ],
    "aliens": [
        "['eyl', 'yuhn', 's']",
        "ALNS"
    ],
    "aligned": [
        "[uh,lahyn,ed]",
        "ALNT"
    ],
    "alignment": [
        "['uh', 'lahyn', 'muhnt']",
        "ALNMNT"
    ],
    "alike": [
        "[uh,lahyk]",
        "ALK"
    ],
    "alive": [
        "['uh', 'lahyv']",
        "ALF"
    ],
    "all": [
        "['awl']",
        "AL"
    ],
    "allah": [
        "['al', 'uh']",
        "AL"
    ],
    "allegations": [
        "['al', 'i', 'gey', 'shuhn', 's']",
        "ALKXNS"
    ],
    "allegiance": [
        "[uh,lee,juhns]",
        "ALJNS"
    ],
    "allen": [
        "['al', 'uhn']",
        "ALN"
    ],
    "aller": [
        "[awl,er]",
        "ALR"
    ],
    "allergic": [
        "['uh', 'lur', 'jik']",
        "ALRJK"
    ],
    "allergies": [
        [
            "al",
            "er",
            "jees"
        ],
        "ALRJS"
    ],
    "alley": [
        "['al', 'ee']",
        "AL"
    ],
    "alleys": [
        "[al,ee,s]",
        "ALS"
    ],
    "alliance": [
        "['uh', 'lahy', 'uhns']",
        "ALNS"
    ],
    "alligator": [
        "['al', 'i', 'gey', 'ter']",
        "ALKTR"
    ],
    "alligators": [
        "['al', 'i', 'gey', 'ter', 's']",
        "ALKTRS"
    ],
    "allow": [
        "[uh,lou]",
        "AL"
    ],
    "allowance": [
        "[uh,lou,uhns]",
        "ALNS"
    ],
    "allowed": [
        "[uh,loud]",
        "ALT"
    ],
    "allure": [
        "[uh,loor]",
        "ALR"
    ],
    "ally": [
        "['verbuh', 'lahy']",
        "AL"
    ],
    "almanac": [
        "[awl,muh,nak]",
        "ALMNK"
    ],
    "almighty": [
        "['awl', 'mahy', 'tee']",
        "ALMT"
    ],
    "almost": [
        "['awl', 'mohst']",
        "ALMST"
    ],
    "alone": [
        "['uh', 'lohn']",
        "ALN"
    ],
    "along": [
        "['uh', 'lawng']",
        "ALNK"
    ],
    "alpha": [
        "[al,fuh]",
        "ALF"
    ],
    "alphabet": [
        "['al', 'fuh', 'bet']",
        "ALFPT"
    ],
    "alphabets": [
        "[al,fuh,bet,s]",
        "ALFPTS"
    ],
    "already": [
        "['awl', 'red', 'ee']",
        "ALRT"
    ],
    "alright": [
        "['awl', 'rahyt']",
        "ALRT"
    ],
    "also": [
        "['awl', 'soh']",
        "ALS"
    ],
    "altar": [
        "[awl,ter]",
        "ALTR"
    ],
    "alter": [
        "[awl,ter]",
        "ALTR"
    ],
    "altitude": [
        "[al,ti,tood]",
        "ALTTT"
    ],
    "aluminum": [
        "[uh,loo,muh,nuhm]",
        "ALMNM"
    ],
    "always": [
        "['awl', 'weyz']",
        "ALS"
    ],
    "am": [
        "['am']",
        "AM"
    ],
    "amaretto": [
        "[am,uh,ret,oh]",
        "AMRT"
    ],
    "amateur": [
        "['am', 'uh', 'choor']",
        "AMTR"
    ],
    "amateurs": [
        "['am', 'uh', 'choor', 's']",
        "AMTRS"
    ],
    "amaze": [
        "['uh', 'meyz']",
        "AMS"
    ],
    "amazed": [
        "['uh', 'meyzd']",
        "AMST"
    ],
    "amazing": [
        "['uh', 'mey', 'zing']",
        "AMSNK"
    ],
    "amazon": [
        "['am', 'uh', 'zon']",
        "AMSN"
    ],
    "amber": [
        "['am', 'ber']",
        "AMPR"
    ],
    "ambiance": [
        "[am,bee,uhns]",
        "AMPNS"
    ],
    "ambidextrous": [
        "[am,bi,dek,struhs]",
        "AMPTKSTRS"
    ],
    "ambition": [
        "['am', 'bish', 'uhn']",
        "AMPXN"
    ],
    "ambitions": [
        "['am', 'bish', 'uhn', 's']",
        "AMPXNS"
    ],
    "ambitious": [
        "['am', 'bish', 'uhs']",
        "AMPTS"
    ],
    "ambulance": [
        "['am', 'byuh', 'luhns']",
        "AMPLNS"
    ],
    "amen": [
        "['ey', 'men']",
        "AMN"
    ],
    "america": [
        "['uh', 'mer', 'i', 'kuh']",
        "AMRK"
    ],
    "america's": [
        "[uh,mer,i,kuh,'s]",
        "AMRKS"
    ],
    "american": [
        "['uh', 'mer', 'i', 'kuhn']",
        "AMRKN"
    ],
    "americans": [
        "[uh,mer,i,kuhn,s]",
        "AMRKNS"
    ],
    "amigo": [
        "['uh', 'mee', 'goh']",
        "AMK"
    ],
    "amigos": [
        "['uh', 'mee', 'goh', 's']",
        "AMKS"
    ],
    "ammo": [
        "['am', 'oh']",
        "AM"
    ],
    "ammunition": [
        "['am', 'yuh', 'nish', 'uhn']",
        "AMNXN"
    ],
    "amnesia": [
        "['am', 'nee', 'zhuh']",
        "AMNS"
    ],
    "amongst": [
        "['uh', 'muhngst']",
        "AMNKST"
    ],
    "amor": [
        "[ey,mawr]",
        "AMR"
    ],
    "amount": [
        "['uh', 'mount']",
        "AMNT"
    ],
    "amounts": [
        "['uh', 'mount', 's']",
        "AMNTS"
    ],
    "amp": [
        "[amp]",
        "AMP"
    ],
    "amphetamine": [
        "[am,fet,uh,meen]",
        "AMFTMN"
    ],
    "amphetamines": [
        "[am,fet,uh,meen,s]",
        "AMFTMNS"
    ],
    "amsterdam": [
        "[am,ster,dam]",
        "AMSTRTM"
    ],
    "amusing": [
        "[uh,myoo,zing]",
        "AMSNK"
    ],
    "an": [
        "['uhn']",
        "AN"
    ],
    "anaconda": [
        "['an', 'uh', 'kon', 'duh']",
        "ANKNT"
    ],
    "anal": [
        "[eyn,l]",
        "ANL"
    ],
    "analyze": [
        "[an,l,ahyz]",
        "ANLS"
    ],
    "anatomy": [
        "[uh,nat,uh,mee]",
        "ANTM"
    ],
    "ancestors": [
        "[an,ses,teror,s]",
        "ANSSTRS"
    ],
    "anchor": [
        "[ang,ker]",
        "ANXR"
    ],
    "and": [
        "['and']",
        "ANT"
    ],
    "anderson": [
        "['an', 'der', 'suhn']",
        "ANTRSN"
    ],
    "andrew": [
        "[an,droo]",
        "ANTR"
    ],
    "anemic": [
        "[uh,nee,mik]",
        "ANMK"
    ],
    "aner": [
        "['eyn', 'r']",
        "ANR"
    ],
    "anesthesia": [
        "[an,uhs,thee,zhuh]",
        "ANS0S"
    ],
    "angel": [
        "['eyn', 'juhl']",
        "ANJL"
    ],
    "angelina": [
        "['an', 'juh', 'lee', 'nuh']",
        "ANJLN"
    ],
    "angels": [
        "['eyn', 'juhl', 's']",
        "ANJLS"
    ],
    "anger": [
        "['ang', 'ger']",
        "ANKR"
    ],
    "angle": [
        "['ang', 'guhl']",
        "ANKL"
    ],
    "angles": [
        "['ang', 'guhl', 's']",
        "ANKLS"
    ],
    "angry": [
        "['ang', 'gree']",
        "ANKR"
    ],
    "angus": [
        "[ang,guhs]",
        "ANKS"
    ],
    "ani": [
        "['ah', 'nee']",
        "AN"
    ],
    "animal": [
        "['an', 'uh', 'muhl']",
        "ANML"
    ],
    "animals": [
        "['an', 'uh', 'muhl', 's']",
        "ANMLS"
    ],
    "animated": [
        "['an', 'uh', 'mey', 'tid']",
        "ANMTT"
    ],
    "animosity": [
        "[an,uh,mos,i,tee]",
        "ANMST"
    ],
    "anita": [
        "['uh', 'nee', 'tuh']",
        "ANT"
    ],
    "ankle": [
        "['ang', 'kuhl']",
        "ANKL"
    ],
    "ankles": [
        "['ang', 'kuhl', 's']",
        "ANKLS"
    ],
    "anna": [
        "['ah', 'nuh']",
        "AN"
    ],
    "anniversary": [
        "['an', 'uh', 'vur', 'suh', 'ree']",
        "ANFRSR"
    ],
    "announcement": [
        "['uh', 'nouns', 'muhnt']",
        "ANNSMNT"
    ],
    "annoying": [
        "['uh', 'noi', 'ing']",
        "ANNK"
    ],
    "anonymous": [
        "[uh,non,uh,muhs]",
        "ANNMS"
    ],
    "another": [
        "['uh', 'nuhth', 'er']",
        "AN0R"
    ],
    "answer": [
        "['an', 'ser']",
        "ANSR"
    ],
    "answered": [
        "[an,ser,ed]",
        "ANSRT"
    ],
    "answering": [
        "['an', 'ser', 'ing']",
        "ANSRNK"
    ],
    "answers": [
        "['an', 'ser', 's']",
        "ANSRS"
    ],
    "ant": [
        "['ant']",
        "ANT"
    ],
    "antarctica": [
        "['ant', 'ahrk', 'ti', 'kuh']",
        "ANTRKTK"
    ],
    "antenna": [
        "[an,ten,uh]",
        "ANTN"
    ],
    "antennas": [
        "['an', 'ten', 'uh', 's']",
        "ANTNS"
    ],
    "anthem": [
        "['an', 'thuhm']",
        "AN0M"
    ],
    "anthems": [
        "[an,thuhm,s]",
        "AN0MS"
    ],
    "anthrax": [
        "[an,thraks]",
        "AN0RKS"
    ],
    "anti": [
        "['an', 'tahy']",
        "ANT"
    ],
    "anticipation": [
        "[an,tis,uh,pey,shuhn]",
        "ANTSPXN"
    ],
    "antidote": [
        "['an', 'ti', 'doht']",
        "ANTTT"
    ],
    "ants": [
        "['ant', 's']",
        "ANTS"
    ],
    "antsy": [
        "['ant', 'see']",
        "ANTS"
    ],
    "anus": [
        "[ey,nuhs]",
        "ANS"
    ],
    "anxiety": [
        "['ang', 'zahy', 'i', 'tee']",
        "ANKST"
    ],
    "anxious": [
        "['angk', 'shuhs']",
        "ANKSS"
    ],
    "any": [
        "['en', 'ee']",
        "AN"
    ],
    "anybody": [
        "['en', 'ee', 'bod', 'ee']",
        "ANPT"
    ],
    "anyhow": [
        "[en,ee,hou]",
        "ANH"
    ],
    "anymore": [
        "['en', 'ee', 'mawr']",
        "ANMR"
    ],
    "anyone": [
        "['en', 'ee', 'wuhn']",
        "ANN"
    ],
    "anything": [
        "['en', 'ee', 'thing']",
        "AN0NK"
    ],
    "anytime": [
        "['en', 'ee', 'tahym']",
        "ANTM"
    ],
    "anyway": [
        "['en', 'ee', 'wey']",
        "AN"
    ],
    "anyways": [
        "[en,ee,weyz]",
        "ANS"
    ],
    "anywhere": [
        "['en', 'ee', 'hwair']",
        "ANR"
    ],
    "apart": [
        "['uh', 'pahrt']",
        "APRT"
    ],
    "apartment": [
        "['uh', 'pahrt', 'muhnt']",
        "APRTMNT"
    ],
    "apartments": [
        "['uh', 'pahrt', 'muhnt', 's']",
        "APRTMNTS"
    ],
    "ape": [
        "['eyp']",
        "AP"
    ],
    "apes": [
        "['eyp', 's']",
        "APS"
    ],
    "apocalypse": [
        "['uh', 'pok', 'uh', 'lips']",
        "APKLPS"
    ],
    "apollo": [
        "[uh,pol,oh]",
        "APL"
    ],
    "apologize": [
        "['uh', 'pol', 'uh', 'jahyz']",
        "APLJS"
    ],
    "apology": [
        "['uh', 'pol', 'uh', 'jee']",
        "APLJ"
    ],
    "app": [
        "['ap']",
        "AP"
    ],
    "appalled": [
        "[uh,pawl,led]",
        "APLT"
    ],
    "apparent": [
        "[uh,par,uhnt]",
        "APRNT"
    ],
    "apparently": [
        "['uh', 'par', 'uhnt', 'ly']",
        "APRNTL"
    ],
    "appeal": [
        "[uh,peel]",
        "APL"
    ],
    "appealing": [
        "['uh', 'pee', 'ling']",
        "APLNK"
    ],
    "appear": [
        "['uh', 'peer']",
        "APR"
    ],
    "appearance": [
        "['uh', 'peer', 'uhns']",
        "APRNS"
    ],
    "appears": [
        "[uh,peer,s]",
        "APRS"
    ],
    "appetite": [
        "['ap', 'i', 'tahyt']",
        "APTT"
    ],
    "applaud": [
        "[uh,plawd]",
        "APLT"
    ],
    "applause": [
        "[uh,plawz]",
        "APLS"
    ],
    "apple": [
        "['ap', 'uhl']",
        "APL"
    ],
    "apples": [
        "[ap,uhlz]",
        "APLS"
    ],
    "application": [
        "[ap,li,key,shuhn]",
        "APLKXN"
    ],
    "applied": [
        "[uh,plahyd]",
        "APLT"
    ],
    "apply": [
        "['uh', 'plahy']",
        "APL"
    ],
    "applying": [
        "[uh,plahy,ing]",
        "APLNK"
    ],
    "appraised": [
        "[uh,preyz,d]",
        "APRST"
    ],
    "appreciate": [
        "['uh', 'pree', 'shee', 'eyt']",
        "APRST"
    ],
    "apprentice": [
        "[uh,pren,tis]",
        "APRNTS"
    ],
    "approach": [
        "['uh', 'prohch']",
        "APRX"
    ],
    "approached": [
        "[uh,prohch,ed]",
        "APRXT"
    ],
    "approaches": [
        "['uh', 'prohch', 'es']",
        "APRXS"
    ],
    "approaching": [
        "['uh', 'prohch', 'ing']",
        "APRXNK"
    ],
    "approval": [
        "[uh,proo,vuhl]",
        "APRFL"
    ],
    "approve": [
        "[uh,proov]",
        "APRF"
    ],
    "approved": [
        "['uh', 'proov', 'd']",
        "APRFT"
    ],
    "april": [
        "['ey', 'pruhl']",
        "APRL"
    ],
    "apron": [
        "['ey', 'pruhn']",
        "APRN"
    ],
    "aqua": [
        "[ak,wuh]",
        "AK"
    ],
    "aquarium": [
        "[uh,kwair,ee,uhm]",
        "AKRM"
    ],
    "aquarius": [
        "[uh,kwair,ee,uhs]",
        "AKRS"
    ],
    "ar": [
        "['rgn']",
        "AR"
    ],
    "arab": [
        "[ar,uhb]",
        "ARP"
    ],
    "arabian": [
        "['uh', 'rey', 'bee', 'uhn']",
        "ARPN"
    ],
    "arcade": [
        "[ahr,keyd]",
        "ARKT"
    ],
    "arch": [
        "[ahrch]",
        "ARX"
    ],
    "are": [
        "['ahr']",
        "AR"
    ],
    "area": [
        "['air', 'ee', 'uh']",
        "AR"
    ],
    "aren't": [
        "['ahrnt']",
        "ARNNT"
    ],
    "arena": [
        "[uh,ree,nuh]",
        "ARN"
    ],
    "arenas": [
        "['uh', 'ree', 'nuh', 's']",
        "ARNS"
    ],
    "argue": [
        "['ahr', 'gyoo']",
        "ARK"
    ],
    "argument": [
        "['ahr', 'gyuh', 'muhnt']",
        "ARKMNT"
    ],
    "arguments": [
        "[ahr,gyuh,muhnt,s]",
        "ARKMNTS"
    ],
    "aria": [
        "[ahr,ee,uh]",
        "AR"
    ],
    "arizona": [
        "[ar,uh,zoh,nuh]",
        "ARSN"
    ],
    "ark": [
        "[ahrk]",
        "ARK"
    ],
    "arm": [
        "['ahrm']",
        "ARM"
    ],
    "arm's": [
        "['ahrm', \"'s\"]",
        "ARMMS"
    ],
    "armageddon": [
        "['ahr', 'muh', 'ged', 'n']",
        "ARMJTN"
    ],
    "armed": [
        "['ahrmd']",
        "ARMT"
    ],
    "arming": [
        "[ahrm,ing]",
        "ARMNK"
    ],
    "armor": [
        "['ahr', 'mer']",
        "ARMR"
    ],
    "arms": [
        "['ahrm', 's']",
        "ARMS"
    ],
    "army": [
        "['ahr', 'mee']",
        "ARM"
    ],
    "arnold": [
        "['ahr', 'nld']",
        "ARNLT"
    ],
    "aroma": [
        "['uh', 'roh', 'muh']",
        "ARM"
    ],
    "around": [
        "['uh', 'round']",
        "ARNT"
    ],
    "aroused": [
        "[uh,rouz,d]",
        "ARST"
    ],
    "arraignment": [
        "[uh,reyn,muhnt]",
        "ARNMNT"
    ],
    "arrange": [
        "[uh,reynj]",
        "ARNJ"
    ],
    "arrangement": [
        "['uh', 'reynj', 'muhnt']",
        "ARNJMNT"
    ],
    "arrangements": [
        "['uh', 'reynj', 'muhnt', 's']",
        "ARNJMNTS"
    ],
    "arrest": [
        "['uh', 'rest']",
        "ARST"
    ],
    "arrested": [
        "['uh', 'rest', 'ed']",
        "ARSTT"
    ],
    "arresting": [
        "['uh', 'res', 'ting']",
        "ARSTNK"
    ],
    "arrival": [
        "['uh', 'rahy', 'vuhl']",
        "ARFL"
    ],
    "arrive": [
        "[uh,rahyv]",
        "ARF"
    ],
    "arrived": [
        "['uh', 'rahyv', 'd']",
        "ARFT"
    ],
    "arrogant": [
        "['ar', 'uh', 'guhnt']",
        "ARKNT"
    ],
    "arrow": [
        "[ar,oh]",
        "AR"
    ],
    "arrows": [
        "['ar', 'oh', 's']",
        "ARS"
    ],
    "arsenal": [
        "[ahr,suh,nl]",
        "ARSNL"
    ],
    "arson": [
        "['ahr', 'suhn']",
        "ARSN"
    ],
    "arsonist": [
        "[ahr,suh,nist]",
        "ARSNST"
    ],
    "art": [
        "['ahrt']",
        "ART"
    ],
    "arthritis": [
        "['ahr', 'thrahy', 'tis']",
        "AR0RTS"
    ],
    "arthur": [
        "['ahr', 'ther']",
        "AR0R"
    ],
    "articles": [
        "['ahr', 'ti', 'kuhl', 's']",
        "ARTKLS"
    ],
    "artillery": [
        "['ahr', 'til', 'uh', 'ree']",
        "ARTLR"
    ],
    "artist": [
        "['ahr', 'tist']",
        "ARTST"
    ],
    "artists": [
        "['ahr', 'tist', 's']",
        "ARTSTS"
    ],
    "arts": [
        "[ahrt,s]",
        "ARTS"
    ],
    "aruba": [
        "['ah', 'roo', 'bah']",
        "ARP"
    ],
    "as": [
        "['az']",
        "AS"
    ],
    "asap": [
        "[ey,sap]",
        "ASP"
    ],
    "ash": [
        "['ash']",
        "AX"
    ],
    "ashamed": [
        "['uh', 'sheymd']",
        "AXMT"
    ],
    "ashanti": [
        "['uh', 'shan', 'tee']",
        "AXNT"
    ],
    "ashes": [
        "['ash', 'es']",
        "AXS"
    ],
    "ashley": [
        "['ash', 'lee']",
        "AXL"
    ],
    "ashton": [
        "['ash', 'tuhn']",
        "AXTN"
    ],
    "ashtray": [
        "[ash,trey]",
        "AXTR"
    ],
    "ashtrays": [
        "[ash,trey,s]",
        "AXTRS"
    ],
    "ashy": [
        "['ash', 'ee']",
        "AX"
    ],
    "asian": [
        "['ey', 'zhuhn']",
        "ASN"
    ],
    "asians": [
        "[ey,zhuhn,s]",
        "ASNS"
    ],
    "aside": [
        "['uh', 'sahyd']",
        "AST"
    ],
    "ask": [
        "['ask']",
        "ASK"
    ],
    "asked": [
        "['ask', 'ed']",
        "ASKT"
    ],
    "asking": [
        "['ask', 'ing']",
        "ASKNK"
    ],
    "asks": [
        "['ask', 's']",
        "ASKS"
    ],
    "asleep": [
        "['uh', 'sleep']",
        "ASLP"
    ],
    "asparagus": [
        "['uh', 'spar', 'uh', 'guhs']",
        "ASPRKS"
    ],
    "aspen": [
        "['as', 'puhn']",
        "ASPN"
    ],
    "asphalt": [
        "['as', 'fawltor']",
        "ASFLT"
    ],
    "aspire": [
        "[uh,spahyuhr]",
        "ASPR"
    ],
    "ass": [
        "['as']",
        "AS"
    ],
    "assassin": [
        "[uh,sas,in]",
        "ASSN"
    ],
    "assassinate": [
        "['uh', 'sas', 'uh', 'neyt']",
        "ASSNT"
    ],
    "assassins": [
        "[uh,sas,in,s]",
        "ASSNS"
    ],
    "assault": [
        "['uh', 'sawlt']",
        "ASLT"
    ],
    "assembly": [
        "[uh,sem,blee]",
        "ASMPL"
    ],
    "asses": [
        "['as', 'iz']",
        "ASS"
    ],
    "asshole": [
        "['as', 'hohl']",
        "ASL"
    ],
    "assholes": [
        "['as', 'hohl', 's']",
        "ASLS"
    ],
    "assignment": [
        "['uh', 'sahyn', 'muhnt']",
        "ASNMNT"
    ],
    "assist": [
        "['uh', 'sist']",
        "ASST"
    ],
    "assistance": [
        "['uh', 'sis', 'tuhns']",
        "ASSTNS"
    ],
    "assistant": [
        "[uh,sis,tuhnt]",
        "ASSTNT"
    ],
    "assists": [
        "['uh', 'sist', 's']",
        "ASSTS"
    ],
    "associate": [
        "[verbuh,soh,shee,eyt]",
        "ASST"
    ],
    "associates": [
        "['verbuh', 'soh', 'shee', 'eyt', 's']",
        "ASSTS"
    ],
    "association": [
        "[uh,soh,see,ey,shuhn]",
        "ASSXN"
    ],
    "assume": [
        "['uh', 'soom']",
        "ASM"
    ],
    "assuming": [
        "[uh,soo,ming]",
        "ASMNK"
    ],
    "assumption": [
        "['uh', 'suhmp', 'shuhn']",
        "ASMPXN"
    ],
    "assumptions": [
        "[uh,suhmp,shuhn,s]",
        "ASMPXNS"
    ],
    "astaire": [
        "[uh,stair]",
        "ASTR"
    ],
    "asthma": [
        "['az', 'muh']",
        "AS0M"
    ],
    "asthmatic": [
        "[az,mat,ik]",
        "AS0MTK"
    ],
    "aston": [
        "['as', 'tuhn']",
        "ASTN"
    ],
    "astonishing": [
        "[uh,ston,i,shing]",
        "ASTNXNK"
    ],
    "astrology": [
        "[uh,strol,uh,jee]",
        "ASTRLJ"
    ],
    "astronaut": [
        "['as', 'truh', 'nawt']",
        "ASTRNT"
    ],
    "astronomical": [
        "['as', 'truh', 'nom', 'i', 'kuhloras', 'truh', 'nom', 'ik']",
        "ASTRNMKL"
    ],
    "asylum": [
        "[uh,sahy,luhm]",
        "ASLM"
    ],
    "at": [
        "['at']",
        "AT"
    ],
    "ate": [
        "['eyt']",
        "AT"
    ],
    "atheist": [
        "[ey,thee,ist]",
        "A0ST"
    ],
    "athlete": [
        "['ath', 'leet']",
        "A0LT"
    ],
    "athletes": [
        "['ath', 'leet', 's']",
        "A0LTS"
    ],
    "athletic": [
        "['ath', 'let', 'ik']",
        "A0LTK"
    ],
    "atlanta": [
        "['at', 'lan', 'tuh']",
        "ATLNT"
    ],
    "atlanta's": [
        "[at,lan,tuh,'s]",
        "ATLNTS"
    ],
    "atlantic": [
        "['at', 'lan', 'tik']",
        "ATLNTK"
    ],
    "atlantis": [
        "['at', 'lan', 'tis']",
        "ATLNTS"
    ],
    "atlas": [
        "[at,luhs]",
        "ATLS"
    ],
    "atmosphere": [
        "['at', 'muhs', 'feer']",
        "ATMSFR"
    ],
    "atom": [
        "[at,uhm]",
        "ATM"
    ],
    "attach": [
        "['uh', 'tach']",
        "ATK"
    ],
    "attached": [
        "['uh', 'tacht']",
        "ATXT"
    ],
    "attack": [
        "['uh', 'tak']",
        "ATK"
    ],
    "attacking": [
        "[uh,tak,ing]",
        "ATKNK"
    ],
    "attempt": [
        "['uh', 'tempt']",
        "ATMPT"
    ],
    "attend": [
        "[uh,tend]",
        "ATNT"
    ],
    "attendance": [
        "['uh', 'ten', 'duhns']",
        "ATNTNS"
    ],
    "attendant": [
        "['uh', 'ten', 'duhnt']",
        "ATNTNT"
    ],
    "attention": [
        "['nounuh', 'ten', 'shuhn']",
        "ATNXN"
    ],
    "attic": [
        "['at', 'ik']",
        "ATK"
    ],
    "attire": [
        "['uh', 'tahyuhr']",
        "ATR"
    ],
    "attitude": [
        "['at', 'i', 'tood']",
        "ATTT"
    ],
    "attitudes": [
        "['at', 'i', 'tood', 's']",
        "ATTTS"
    ],
    "attorney": [
        "[uh,tur,nee]",
        "ATRN"
    ],
    "attract": [
        "['uh', 'trakt']",
        "ATRKT"
    ],
    "attracted": [
        "['uh', 'trakt', 'ed']",
        "ATRKTT"
    ],
    "attraction": [
        "[uh,trak,shuhn]",
        "ATRKXN"
    ],
    "attractive": [
        "['uh', 'trak', 'tiv']",
        "ATRKTF"
    ],
    "au": [
        "[oh]",
        "A"
    ],
    "auction": [
        "['awk', 'shuhn']",
        "AKXN"
    ],
    "audible": [
        "[aw,duh,buhl]",
        "ATPL"
    ],
    "audience": [
        "[aw,dee,uhns]",
        "ATNS"
    ],
    "audio": [
        "[aw,dee,oh]",
        "AT"
    ],
    "audition": [
        "[aw,dish,uhn]",
        "ATXN"
    ],
    "august": [
        "['aw', 'guhst']",
        "AKST"
    ],
    "aunt": [
        "['ant']",
        "ANT"
    ],
    "auntie": [
        "['an', 'tee']",
        "ANT"
    ],
    "aunties": [
        "[an,tee,s]",
        "ANTS"
    ],
    "aunts": [
        "[ant,s]",
        "ANTS"
    ],
    "aunty": [
        "['an', 'tee']",
        "ANT"
    ],
    "aura": [
        "['awr', 'uh']",
        "AR"
    ],
    "aurora": [
        "[uh,rawr,uh]",
        "ARR"
    ],
    "austin": [
        "['aw', 'stuhn']",
        "ASTN"
    ],
    "australia": [
        "[aw,streyl,yuh]",
        "ASTRL"
    ],
    "authentic": [
        "[aw,then,tik]",
        "A0NTK"
    ],
    "author": [
        "['aw', 'ther']",
        "A0R"
    ],
    "authority": [
        "[uh,thawr,i,tee]",
        "A0RT"
    ],
    "auto": [
        "['aw', 'toh']",
        "AT"
    ],
    "autobahn": [
        "[aw,tuh,bahn]",
        "ATPN"
    ],
    "autobiography": [
        "['aw', 'tuh', 'bahy', 'og', 'ruh', 'fee']",
        "ATPKRF"
    ],
    "autograph": [
        "['aw', 'tuh', 'graf']",
        "ATKRF"
    ],
    "automatic": [
        "['aw', 'tuh', 'mat', 'ik']",
        "ATMTK"
    ],
    "automatically": [
        "[aw,tuh,mat,ik,lee]",
        "ATMTKL"
    ],
    "automatics": [
        "[aw,tuh,mat,ik,s]",
        "ATMTKS"
    ],
    "automobiles": [
        "['aw', 'tuh', 'muh', 'beel', 's']",
        "ATMPLS"
    ],
    "autos": [
        "[aw,toh,s]",
        "ATS"
    ],
    "autumn": [
        "[aw,tuhm]",
        "ATMN"
    ],
    "av": [
        "[ahv]",
        "AF"
    ],
    "available": [
        "['uh', 'vey', 'luh', 'buhl']",
        "AFLPL"
    ],
    "avalanche": [
        "['av', 'uh', 'lanch']",
        "AFLNX"
    ],
    "avatar": [
        "['av', 'uh', 'tahr']",
        "AFTR"
    ],
    "ave": [
        "['ah', 'vey']",
        "AF"
    ],
    "avenue": [
        "['av', 'uh', 'nyoo']",
        "AFN"
    ],
    "average": [
        "['av', 'er', 'ij']",
        "AFRJ"
    ],
    "aviator": [
        "[ey,vee,ey,ter]",
        "AFTR"
    ],
    "aviators": [
        "[ey,vee,ey,ter,s]",
        "AFTRS"
    ],
    "avoid": [
        "[uh,void]",
        "AFT"
    ],
    "aw": [
        "['aw']",
        "A"
    ],
    "await": [
        "['uh', 'weyt']",
        "AT"
    ],
    "awaits": [
        "[uh,weyt,s]",
        "ATS"
    ],
    "awake": [
        "['uh', 'weyk']",
        "AK"
    ],
    "award": [
        "[uh,wawrd]",
        "ART"
    ],
    "awards": [
        "[uh,wawrd,s]",
        "ARTS"
    ],
    "aware": [
        "['uh', 'wair']",
        "AR"
    ],
    "away": [
        "['uh', 'wey']",
        "A"
    ],
    "awe": [
        "[aw]",
        "A"
    ],
    "awesome": [
        "['aw', 'suhm']",
        "ASM"
    ],
    "awful": [
        "[aw,fuhl]",
        "AFL"
    ],
    "awfully": [
        "[aw,fuh,lee]",
        "AFL"
    ],
    "awhile": [
        "[uh,hwahyl]",
        "AL"
    ],
    "awkward": [
        "['awk', 'werd']",
        "AKRT"
    ],
    "awol": [
        "['pronouncedasinitialsorey', 'wawl']",
        "AL"
    ],
    "axe": [
        "['aks', 'e']",
        "AKS"
    ],
    "axis": [
        "[ak,sis]",
        "AKSS"
    ],
    "aye": [
        "['ahy']",
        "A"
    ],
    "azure": [
        "[azh,er]",
        "ASR"
    ],
    "b": [
        "['bee', '']",
        "P"
    ],
    "ba": [
        "['bah']",
        "P"
    ],
    "baba": [
        "[bah,buh]",
        "PP"
    ],
    "babble": [
        "[bab,uhl]",
        "PPL"
    ],
    "babe": [
        "['beyb']",
        "PP"
    ],
    "babes": [
        "['beyb', 's']",
        "PPS"
    ],
    "baboon": [
        "['ba', 'boonor']",
        "PPN"
    ],
    "baby": [
        "['bey', 'bee']",
        "PP"
    ],
    "baby's": [
        "[bey,bee,'s]",
        "PPS"
    ],
    "babylon": [
        "['bab', 'uh', 'luhn']",
        "PPLN"
    ],
    "bach": [
        "['bach']",
        "PK"
    ],
    "bachelor": [
        "['bach', 'uh', 'ler']",
        "PXLR"
    ],
    "back": [
        "['bak']",
        "PK"
    ],
    "back's": [
        "['bak', \"'s\"]",
        "PKK"
    ],
    "backboard": [
        "['bak', 'bawrd']",
        "PKPRT"
    ],
    "backed": [
        "[bakt]",
        "PKT"
    ],
    "backflip": [
        "['bak', 'flip']",
        "PKFLP"
    ],
    "background": [
        "['bak', 'ground']",
        "PKKRNT"
    ],
    "backing": [
        "['bak', 'ing']",
        "PKNK"
    ],
    "backpack": [
        "['bak', 'pak']",
        "PKPK"
    ],
    "backpackers": [
        "[bak,pak,ers]",
        "PKPKRS"
    ],
    "backs": [
        "['bak', 's']",
        "PKS"
    ],
    "backseat": [
        "['bak', 'seet']",
        "PKST"
    ],
    "backseats": [
        "[bak,seet,s]",
        "PKSTS"
    ],
    "backside": [
        "['bak', 'sahyd']",
        "PKST"
    ],
    "backstabbed": [
        "['bak', 'stab', 'bed']",
        "PKSTPT"
    ],
    "backstabbing": [
        "['bak', 'stab', 'bing']",
        "PKSTPNK"
    ],
    "backstage": [
        "['bak', 'steyj']",
        "PKSTJ"
    ],
    "backstreet": [
        [
            "bak",
            "street"
        ],
        "PKSTRT"
    ],
    "backstroke": [
        "['bak', 'strohk']",
        "PKSTRK"
    ],
    "backtrack": [
        "[bak,trak]",
        "PKTRK"
    ],
    "backup": [
        "['bak', 'uhp']",
        "PKP"
    ],
    "backwards": [
        "['bak', 'werd', 's']",
        "PKRTS"
    ],
    "backwood": [
        "['bak', 'woodz', '']",
        "PKT"
    ],
    "backwoods": [
        "['bak', 'woodz']",
        "PKTS"
    ],
    "backyard": [
        "['bak', 'yahrd']",
        "PKRT"
    ],
    "bacon": [
        "['bey', 'kuhn']",
        "PKN"
    ],
    "bad": [
        "['bad']",
        "PT"
    ],
    "badder": [
        "['bad', 'er']",
        "PTR"
    ],
    "baddest": [
        "['bad', 'ist']",
        "PTST"
    ],
    "baddies": [
        "['bad', 'ee', 's']",
        "PTS"
    ],
    "badge": [
        "[baj]",
        "PJ"
    ],
    "badges": [
        "[baj,s]",
        "PJS"
    ],
    "badly": [
        "[bad,lee]",
        "PTL"
    ],
    "bae": [
        "['bey']",
        "P"
    ],
    "bag": [
        "['bag']",
        "PK"
    ],
    "bagel": [
        "['bey', 'guhl']",
        "PJL"
    ],
    "baggage": [
        "[bag,ij]",
        "PKJ"
    ],
    "bagged": [
        "['bag', 'ged']",
        "PKT"
    ],
    "bagging": [
        "['bag', 'ing']",
        "PJNK"
    ],
    "baggy": [
        "['bag', 'ee']",
        "PK"
    ],
    "baghdad": [
        "[bag,dad]",
        "PTT"
    ],
    "bags": [
        "['bag', 's']",
        "PKS"
    ],
    "baguettes": [
        "['ba', 'get', 's']",
        "PKTS"
    ],
    "bahamas": [
        "['buh', 'hah', 'muhz']",
        "PHMS"
    ],
    "bail": [
        "['beyl']",
        "PL"
    ],
    "bailed": [
        "['beyl', 'ed']",
        "PLT"
    ],
    "bailey": [
        "[bey,lee]",
        "PL"
    ],
    "baileys": [
        "[bey,lee,s]",
        "PLS"
    ],
    "bailing": [
        "[beyl,ing]",
        "PLNK"
    ],
    "bails": [
        "['beyl', 's']",
        "PLS"
    ],
    "bait": [
        "[beyt]",
        "PT"
    ],
    "bake": [
        "['beyk']",
        "PK"
    ],
    "baked": [
        "['beyk', 'd']",
        "PKT"
    ],
    "baker": [
        "['bey', 'ker']",
        "PKR"
    ],
    "baker's": [
        "[bey,ker,'s]",
        "PKRRS"
    ],
    "bakers": [
        "[bey,ker,s]",
        "PKRS"
    ],
    "bakery": [
        "[bey,kuh,ree]",
        "PKR"
    ],
    "baking": [
        [
            "bah",
            "king"
        ],
        "PKNK"
    ],
    "balance": [
        "['bal', 'uhns']",
        "PLNS"
    ],
    "balboa": [
        "['bal', 'boh', 'uh']",
        "PLP"
    ],
    "balcony": [
        "['bal', 'kuh', 'nee']",
        "PLKN"
    ],
    "bald": [
        "['bawld']",
        "PLT"
    ],
    "balding": [
        "[bawld,ing]",
        "PLTNK"
    ],
    "bale": [
        "['beyl']",
        "PL"
    ],
    "balenciaga": [
        "['buh', 'len', 'see', 'ah', 'guh']",
        "PLNSK"
    ],
    "bales": [
        "['beyl', 's']",
        "PLS"
    ],
    "bali": [
        "[bah,lee]",
        "PL"
    ],
    "ball": [
        "['bawl']",
        "PL"
    ],
    "balled": [
        "[bawl,ed]",
        "PLT"
    ],
    "baller": [
        "['bawl', 'er']",
        "PLR"
    ],
    "ballerina": [
        "[bal,uh,ree,nuh]",
        "PLRN"
    ],
    "ballers": [
        "['bawl', 'ers']",
        "PLRS"
    ],
    "ballet": [
        "['ba', 'ley']",
        "PLT"
    ],
    "balling": [
        "['bawl', 'ing']",
        "PLNK"
    ],
    "ballistic": [
        "['buh', 'lis', 'tik']",
        "PLSTK"
    ],
    "balloon": [
        "['buh', 'loon']",
        "PLN"
    ],
    "balloons": [
        "[buh,loon,s]",
        "PLNS"
    ],
    "ballpark": [
        "[bawl,pahrk]",
        "PLPRK"
    ],
    "ballplayer": [
        "['bawl', 'pley', 'er']",
        "PLPLR"
    ],
    "balls": [
        "['bawl', 's']",
        "PLS"
    ],
    "bally": [
        "[bal,ee]",
        "PL"
    ],
    "balmain": [
        "['bal', 'man']",
        "PLMN"
    ],
    "balmains": [
        [
            "bal",
            "meynz"
        ],
        "PLMNS"
    ],
    "bam": [
        "[bam]",
        "PM"
    ],
    "bama": [
        "['bam', 'uh']",
        "PM"
    ],
    "bambi": [
        "['bam', 'bee']",
        "PMP"
    ],
    "bamboo": [
        "['bam', 'boo']",
        "PMP"
    ],
    "ban": [
        "['ban']",
        "PN"
    ],
    "banana": [
        "['buh', 'nan', 'uh']",
        "PNN"
    ],
    "bananas": [
        "['buh', 'nan', 'uhz']",
        "PNNS"
    ],
    "band": [
        "['band']",
        "PNT"
    ],
    "bandage": [
        "['ban', 'dij']",
        "PNTJ"
    ],
    "bandages": [
        "[ban,dij,s]",
        "PNTJS"
    ],
    "bandanna": [
        "['ban', 'dan', 'uh']",
        "PNTN"
    ],
    "bandannas": [
        "['ban', 'dan', 'uh', 's']",
        "PNTNS"
    ],
    "bandicoot": [
        "['ban', 'di', 'koot']",
        "PNTKT"
    ],
    "bandit": [
        "['ban', 'dit']",
        "PNTT"
    ],
    "bando": [
        [
            "ban",
            "doo"
        ],
        "PNT"
    ],
    "bands": [
        "['band', 's']",
        "PNTS"
    ],
    "bandwagon": [
        "['band', 'wag', 'uhn']",
        "PNTKN"
    ],
    "bang": [
        "['bang']",
        "PNK"
    ],
    "banged": [
        "[bang,ed]",
        "PNJT"
    ],
    "banger": [
        "['bang', 'er']",
        "PNKR"
    ],
    "bangers": [
        "['bang', 'er', 's']",
        "PNKRS"
    ],
    "banging": [
        "['bang', 'ing']",
        "PNJNK"
    ],
    "bangles": [
        "[bang,guhl,s]",
        "PNKLS"
    ],
    "bangs": [
        "['bangz']",
        "PNKS"
    ],
    "banister": [
        "['ban', 'uh', 'ster']",
        "PNSTR"
    ],
    "bank": [
        "['bangk']",
        "PNK"
    ],
    "bankbook": [
        "[bangk,book]",
        "PNKPK"
    ],
    "banker": [
        "['bang', 'ker']",
        "PNKR"
    ],
    "bankhead": [
        "['bangk', 'hed']",
        "PNKT"
    ],
    "banking": [
        "['bang', 'king']",
        "PNKNK"
    ],
    "bankroll": [
        "['bangk', 'rohl']",
        "PNKRL"
    ],
    "bankrolls": [
        "[bangk,rohl,s]",
        "PNKRLS"
    ],
    "bankrupt": [
        "[bangk,ruhpt]",
        "PNKRPT"
    ],
    "banks": [
        "[bangks]",
        "PNKS"
    ],
    "banned": [
        "[ban,ned]",
        "PNT"
    ],
    "banner": [
        "[ban,er]",
        "PNR"
    ],
    "banquet": [
        "['bang', 'kwit']",
        "PNKT"
    ],
    "bans": [
        "[banz]",
        "PNS"
    ],
    "banshee": [
        "['ban', 'shee']",
        "PNX"
    ],
    "bap": [
        "[bap]",
        "PP"
    ],
    "baptism": [
        "[bap,tiz,uhm]",
        "PPTSM"
    ],
    "baptist": [
        "['bap', 'tist']",
        "PPTST"
    ],
    "baptized": [
        "['bap', 'tahyz', 'd']",
        "PPTST"
    ],
    "bar": [
        "['bahr']",
        "PR"
    ],
    "barbarian": [
        "[bahr,bair,ee,uhn]",
        "PRPRN"
    ],
    "barbecue": [
        "['bahr', 'bi', 'kyoo']",
        "PRPK"
    ],
    "barbecued": [
        "[bahr,bi,kyoo,d]",
        "PRPKT"
    ],
    "barbell": [
        "[bahr,bel]",
        "PRPL"
    ],
    "barbeque": [
        "[bahr,bi,kyoo]",
        "PRPK"
    ],
    "barber": [
        "['bahr', 'ber']",
        "PRPR"
    ],
    "barbers": [
        "[bahr,ber,s]",
        "PRPRS"
    ],
    "barbershop": [
        "['bahr', 'ber', 'shop']",
        "PRPRXP"
    ],
    "barbie": [
        "['bahr', 'bee']",
        "PRP"
    ],
    "barbies": [
        "['bahr', 'bee', 's']",
        "PRPS"
    ],
    "barbwire": [
        "['bahrb', 'wahyuhr']",
        "PRPR"
    ],
    "bare": [
        "['bair']",
        "PR"
    ],
    "barefoot": [
        "[bair,foot]",
        "PRFT"
    ],
    "barely": [
        "['bair', 'lee']",
        "PRL"
    ],
    "barfing": [
        "[bahrf,ing]",
        "PRFNK"
    ],
    "bargain": [
        "[bahr,guhn]",
        "PRKN"
    ],
    "bari": [
        "['bahr', 'ee']",
        "PR"
    ],
    "baritone": [
        "[bar,i,tohn]",
        "PRTN"
    ],
    "bark": [
        "[bahrk]",
        "PRK"
    ],
    "barker": [
        "['bahr', 'ker']",
        "PRKR"
    ],
    "barking": [
        "['bahr', 'king']",
        "PRKNK"
    ],
    "barkley": [
        "['bahrk', 'lee']",
        "PRKL"
    ],
    "barn": [
        "[bahrn]",
        "PRN"
    ],
    "barred": [
        "['bahrd']",
        "PRT"
    ],
    "barrel": [
        "['bar', 'uhl']",
        "PRL"
    ],
    "barrels": [
        "[bar,uhl,s]",
        "PRLS"
    ],
    "barrier": [
        "['bar', 'ee', 'er']",
        "PR"
    ],
    "barrio": [
        "[bahr,ee,oh]",
        "PR"
    ],
    "barry": [
        "['bar', 'ee']",
        "PR"
    ],
    "bars": [
        "['bahr', 's']",
        "PRS"
    ],
    "bart": [
        "[bahrt]",
        "PRT"
    ],
    "bartender": [
        "['bahr', 'ten', 'der']",
        "PRTNTR"
    ],
    "base": [
        "['beys']",
        "PS"
    ],
    "baseball": [
        "['beys', 'bawl']",
        "PSPL"
    ],
    "based": [
        "['beys', 'd']",
        "PST"
    ],
    "baseline": [
        "[beys,lahyn]",
        "PSLN"
    ],
    "basement": [
        "['beys', 'muhnt']",
        "PSMNT"
    ],
    "basements": [
        "[beys,muhnt,s]",
        "PSMNTS"
    ],
    "bases": [
        "[bey,seez]",
        "PSS"
    ],
    "bashing": [
        "['bash', 'ing']",
        "PXNK"
    ],
    "basic": [
        "['bey', 'sik']",
        "PSK"
    ],
    "basically": [
        "['bey', 'sik', 'lee']",
        "PSKL"
    ],
    "basics": [
        "[bey,sik,s]",
        "PSKS"
    ],
    "basis": [
        "[bey,sis]",
        "PSS"
    ],
    "basket": [
        "['bas', 'kit']",
        "PSKT"
    ],
    "basketball": [
        "['bas', 'kit', 'bawl']",
        "PSKTPL"
    ],
    "baskets": [
        "[bas,kit,s]",
        "PSKTS"
    ],
    "bass": [
        "['beys']",
        "PS"
    ],
    "bastard": [
        "['bas', 'terd']",
        "PSTRT"
    ],
    "bastards": [
        "['bas', 'terd', 's']",
        "PSTRTS"
    ],
    "bat": [
        "['bat']",
        "PT"
    ],
    "batch": [
        "['bach']",
        "PX"
    ],
    "bate": [
        "[beyt]",
        "PT"
    ],
    "bates": [
        "[beyts]",
        "PTS"
    ],
    "bath": [
        "['bath']",
        "P0"
    ],
    "bathe": [
        "[beyth]",
        "P0"
    ],
    "bathing": [
        "['bath', 'ing']",
        "P0NK"
    ],
    "bathroom": [
        "['bath', 'room']",
        "P0RM"
    ],
    "bathrooms": [
        "['bath', 'room', 's']",
        "P0RMS"
    ],
    "bathtub": [
        "['bath', 'tuhb']",
        "P0TP"
    ],
    "batman": [
        "[bat,muhn]",
        "PTMN"
    ],
    "baton": [
        "[buh,ton]",
        "PTN"
    ],
    "bats": [
        "[bats]",
        "PTS"
    ],
    "batted": [
        "['bat', 'ted']",
        "PTT"
    ],
    "batter": [
        "[bat,er]",
        "PTR"
    ],
    "batteries": [
        "[bat,uh,ree,s]",
        "PTRS"
    ],
    "battery": [
        "['bat', 'uh', 'ree']",
        "PTR"
    ],
    "battle": [
        "['bat', 'l']",
        "PTL"
    ],
    "battle's": [
        "[bat,l,'s]",
        "PTLS"
    ],
    "battlefield": [
        "['bat', 'l', 'feeld']",
        "PTLFLT"
    ],
    "battles": [
        "['bat', 'l', 's']",
        "PTLS"
    ],
    "battleship": [
        "[bat,l,ship]",
        "PTLXP"
    ],
    "bay": [
        "['bey']",
        "P"
    ],
    "bayou": [
        "['bahy', 'oo']",
        "P"
    ],
    "bb": [
        "[bee,bee]",
        "P"
    ],
    "bbs": [
        "[bee,bee]",
        "PS"
    ],
    "be": [
        "['bee']",
        "P"
    ],
    "beach": [
        "['beech']",
        "PX"
    ],
    "beaches": [
        "['beech', 'es']",
        "PXS"
    ],
    "beads": [
        "['beed', 's']",
        "PTS"
    ],
    "beam": [
        "['beem']",
        "PM"
    ],
    "beaming": [
        "['bee', 'ming']",
        "PMNK"
    ],
    "beams": [
        "['beem', 's']",
        "PMS"
    ],
    "bean": [
        "['been']",
        "PN"
    ],
    "beanie": [
        "['bee', 'nee']",
        "PN"
    ],
    "beans": [
        "['been', 's']",
        "PNS"
    ],
    "bear": [
        "['bair']",
        "PR"
    ],
    "beard": [
        "[beerd]",
        "PRT"
    ],
    "bearer": [
        "[bair,er]",
        "PRR"
    ],
    "bearing": [
        "[bair,ing]",
        "PRNK"
    ],
    "bears": [
        "['bair', 's']",
        "PRS"
    ],
    "beast": [
        "['beest']",
        "PST"
    ],
    "beat": [
        "['beet']",
        "PT"
    ],
    "beaten": [
        "[beet,n]",
        "PTN"
    ],
    "beater": [
        "['bee', 'ter']",
        "PTR"
    ],
    "beaters": [
        "['bee', 'ter', 's']",
        "PTRS"
    ],
    "beating": [
        "['bee', 'ting']",
        "PTNK"
    ],
    "beatles": [
        "['beet', 'lz']",
        "PTLS"
    ],
    "beats": [
        "['beet', 's']",
        "PTS"
    ],
    "beaucoup": [
        "['boh', 'koo']",
        "PKP"
    ],
    "beautiful": [
        "['byoo', 'tuh', 'fuhl']",
        "PTFL"
    ],
    "beauty": [
        "['byoo', 'tee']",
        "PT"
    ],
    "beaver": [
        "['bee', 'ver']",
        "PFR"
    ],
    "became": [
        "['bih', 'keym']",
        "PKM"
    ],
    "because": [
        "['bih', 'kawz']",
        "PKS"
    ],
    "becky": [
        "['bek', 'ee']",
        "PK"
    ],
    "become": [
        "['bih', 'kuhm']",
        "PKM"
    ],
    "becoming": [
        "[bih,kuhm,ing]",
        "PKMNK"
    ],
    "bed": [
        "['bed']",
        "PT"
    ],
    "bedrock": [
        "['bed', 'rok']",
        "PTRK"
    ],
    "bedroom": [
        "['bed', 'room']",
        "PTRM"
    ],
    "bedrooms": [
        "[bed,room,s]",
        "PTRMS"
    ],
    "beds": [
        "[bedz]",
        "PTS"
    ],
    "bedtime": [
        "['bed', 'tahym']",
        "PTM"
    ],
    "bee": [
        "['bee']",
        "P"
    ],
    "bee's": [
        "['bee', \"'s\"]",
        "PS"
    ],
    "beef": [
        "['beef']",
        "PF"
    ],
    "beefing": [
        "['beef', 'ing']",
        "PFNK"
    ],
    "beefs": [
        "[beef,s]",
        "PFS"
    ],
    "been": [
        "['bin']",
        "PN"
    ],
    "beep": [
        "['beep']",
        "PP"
    ],
    "beeped": [
        "[beep,ed]",
        "PPT"
    ],
    "beeper": [
        "['bee', 'per']",
        "PPR"
    ],
    "beepers": [
        "[bee,per,s]",
        "PPRS"
    ],
    "beer": [
        "['beer']",
        "PR"
    ],
    "beers": [
        "['beerz']",
        "PRS"
    ],
    "bees": [
        "['bee', 's']",
        "PS"
    ],
    "beetle": [
        "['beet', 'l']",
        "PTL"
    ],
    "beetlejuice": [
        [
            "beet",
            "l",
            "joos"
        ],
        "PTLJS"
    ],
    "beetles": [
        "['beet', 'l', 's']",
        "PTLS"
    ],
    "before": [
        "['bih', 'fawr']",
        "PFR"
    ],
    "beg": [
        "['beg']",
        "PK"
    ],
    "began": [
        "['bih', 'gan']",
        "PKN"
    ],
    "begging": [
        "['beg', 'ging']",
        "PKNK"
    ],
    "beging": [
        [
            "beg",
            "ing"
        ],
        "PJNK"
    ],
    "beginner": [
        "['bih', 'gin', 'er']",
        "PJNR"
    ],
    "beginners": [
        "['bih', 'gin', 'er', 's']",
        "PJNRS"
    ],
    "beginning": [
        "['bih', 'gin', 'ing']",
        "PJNNK"
    ],
    "beginnings": [
        "[bih,gin,ing,s]",
        "PJNNKS"
    ],
    "begins": [
        "[bih,gin,s]",
        "PJNS"
    ],
    "begun": [
        "['bih', 'guhn']",
        "PKN"
    ],
    "behalf": [
        "['bih', 'haf']",
        "PHLF"
    ],
    "behave": [
        "['bih', 'heyv']",
        "PHF"
    ],
    "behavior": [
        "['bih', 'heyv', 'yer']",
        "PHFR"
    ],
    "behead": [
        "[bih,hed]",
        "PHT"
    ],
    "behind": [
        "['bih', 'hahynd']",
        "PHNT"
    ],
    "behold": [
        "[bih,hohld]",
        "PHLT"
    ],
    "beholder": [
        "[bih,hohld,er]",
        "PHLTR"
    ],
    "beige": [
        "[beyzh]",
        "PJ"
    ],
    "beijing": [
        "[bey,jing]",
        "PJNK"
    ],
    "being": [
        "['bee', 'ing']",
        "PNK"
    ],
    "beings": [
        "['bee', 'ing', 's']",
        "PNKS"
    ],
    "bel": [
        "[bel]",
        "PL"
    ],
    "belated": [
        "[bih,ley,tid]",
        "PLTT"
    ],
    "belief": [
        "[bih,leef]",
        "PLF"
    ],
    "believe": [
        "['bih', 'leev']",
        "PLF"
    ],
    "believed": [
        "['bih', 'leev', 'd']",
        "PLFT"
    ],
    "believer": [
        "[bih,leev,r]",
        "PLFR"
    ],
    "believers": [
        "[bih,leev,rs]",
        "PLFRS"
    ],
    "belittle": [
        "[bih,lit,l]",
        "PLTL"
    ],
    "bell": [
        "['bel']",
        "PL"
    ],
    "bells": [
        "[belz]",
        "PLS"
    ],
    "belly": [
        "['bel', 'ee']",
        "PL"
    ],
    "belong": [
        "['bih', 'lawng']",
        "PLNK"
    ],
    "belongs": [
        "['bih', 'lawng', 's']",
        "PLNKS"
    ],
    "beloved": [
        "['bih', 'luhv', 'id']",
        "PLFT"
    ],
    "below": [
        "['bih', 'loh']",
        "PL"
    ],
    "belt": [
        "['belt']",
        "PLT"
    ],
    "belts": [
        "['belt', 's']",
        "PLTS"
    ],
    "belvedere": [
        "[bel,vi,deer]",
        "PLFTR"
    ],
    "belvederes": [
        "[bel,vi,deer,s]",
        "PLFTRS"
    ],
    "ben": [
        "['ben']",
        "PN"
    ],
    "bench": [
        "['bench']",
        "PNX"
    ],
    "benches": [
        "[bench,es]",
        "PNXS"
    ],
    "bend": [
        "['bend']",
        "PNT"
    ],
    "bending": [
        "['bend', 'ing']",
        "PNTNK"
    ],
    "bends": [
        "['bend', 's']",
        "PNTS"
    ],
    "beneath": [
        "['bih', 'neeth']",
        "PN0"
    ],
    "beneficial": [
        "[ben,uh,fish,uhl]",
        "PNFSL"
    ],
    "benefit": [
        "['ben', 'uh', 'fit']",
        "PNFT"
    ],
    "benefits": [
        "[ben,uh,fit,s]",
        "PNFTS"
    ],
    "bengal": [
        "[ben,gawl]",
        "PNKL"
    ],
    "benjamin": [
        "['ben', 'juh', 'muhn']",
        "PNJMN"
    ],
    "benjamin's": [
        "['ben', 'juh', 'muhn', \"'s\"]",
        "PNJMNNS"
    ],
    "benjamins": [
        "['ben', 'juh', 'muhn', 's']",
        "PNJMNS"
    ],
    "bennett": [
        "[ben,it]",
        "PNT"
    ],
    "benny": [
        "['ben', 'ee']",
        "PN"
    ],
    "bens": [
        "['ben', 's']",
        "PNS"
    ],
    "bent": [
        "['bent']",
        "PNT"
    ],
    "bentley": [
        "['bent', 'lee']",
        "PNTL"
    ],
    "beretta": [
        "['buh', 'ret', 'uh']",
        "PRT"
    ],
    "berettas": [
        "['buh', 'ret', 'uh', 's']",
        "PRTS"
    ],
    "berg": [
        "['burg']",
        "PRK"
    ],
    "berks": [
        "[burk,sheer,]",
        "PRKS"
    ],
    "berlin": [
        "['ber', 'lin']",
        "PRLN"
    ],
    "bermuda": [
        "[ber,myoo,duh]",
        "PRMT"
    ],
    "berry": [
        "['ber', 'ee']",
        "PR"
    ],
    "berserk": [
        "['ber', 'surk']",
        "PRSRK"
    ],
    "beside": [
        "['bih', 'sahyd']",
        "PST"
    ],
    "besides": [
        "['bih', 'sahydz']",
        "PSTS"
    ],
    "best": [
        "['best']",
        "PST"
    ],
    "bestest": [
        "['bes', 'tist']",
        "PSTST"
    ],
    "bestie": [
        "['bes', 'tee']",
        "PST"
    ],
    "bet": [
        "['bet']",
        "PT"
    ],
    "betray": [
        "['bih', 'trey']",
        "PTR"
    ],
    "betrayed": [
        "['bih', 'trey', 'ed']",
        "PTRT"
    ],
    "bets": [
        "[bet,s]",
        "PTS"
    ],
    "betta": [
        "['bet', 'uh']",
        "PT"
    ],
    "better": [
        "['bet', 'er']",
        "PTR"
    ],
    "betting": [
        "['bet', 'ting']",
        "PTNK"
    ],
    "between": [
        "['bih', 'tween']",
        "PTN"
    ],
    "beverage": [
        "[bev,er,ij]",
        "PFRJ"
    ],
    "beverly": [
        "['bev', 'er', 'lee']",
        "PFRL"
    ],
    "beware": [
        "[bih,wair]",
        "PR"
    ],
    "beyond": [
        "['bee', 'ond']",
        "PNT"
    ],
    "bezel": [
        "['bez', 'uhl']",
        "PSL"
    ],
    "bezels": [
        "[bez,uhl,s]",
        "PSLS"
    ],
    "bi": [
        "['bahy']",
        "P"
    ],
    "bias": [
        "[bahy,uhs]",
        "PS"
    ],
    "biased": [
        "['bahy', 'uhst']",
        "PST"
    ],
    "bib": [
        "[bib]",
        "PP"
    ],
    "bible": [
        "['bahy', 'buhl']",
        "PPL"
    ],
    "bibles": [
        "['bahy', 'buhl', 's']",
        "PPLS"
    ],
    "biblical": [
        "[bib,li,kuhl]",
        "PPLKL"
    ],
    "biceps": [
        "[bahy,seps]",
        "PSPS"
    ],
    "bickering": [
        "['bik', 'er', 'ing']",
        "PKRNK"
    ],
    "bicoastal": [
        "['bahy', 'kohs', 'tl']",
        "PKSTL"
    ],
    "bicycle": [
        "['bahy', 'si', 'kuhl']",
        "PSKL"
    ],
    "bicycles": [
        "[bahy,si,kuhl,s]",
        "PSKLS"
    ],
    "bid": [
        "['bid']",
        "PT"
    ],
    "bidding": [
        "['bid', 'ing']",
        "PTNK"
    ],
    "biddy": [
        "['bid', 'ee']",
        "PT"
    ],
    "big": [
        "['big']",
        "PK"
    ],
    "bigger": [
        "['big', 'ger']",
        "PKR"
    ],
    "biggest": [
        "['big', 'gest']",
        "PKST"
    ],
    "biggie": [
        "['big', 'ee']",
        "PK"
    ],
    "bike": [
        "['bahyk']",
        "PK"
    ],
    "biker": [
        "['bahy', 'ker']",
        "PKR"
    ],
    "bikes": [
        "[bahyk,s]",
        "PKS"
    ],
    "bikini": [
        "['bih', 'kee', 'nee']",
        "PKN"
    ],
    "bikinis": [
        "[bih,kee,nee,s]",
        "PKNS"
    ],
    "bilingual": [
        "[bahy,ling,gwuhlor]",
        "PLNKL"
    ],
    "bill": [
        "['bil']",
        "PL"
    ],
    "billboard": [
        "['bil', 'bawrd']",
        "PLPRT"
    ],
    "billion": [
        "['bil', 'yuhn']",
        "PLN"
    ],
    "billionaire": [
        "['bil', 'yuh', 'nair']",
        "PLNR"
    ],
    "billions": [
        "['bil', 'yuhn', 's']",
        "PLNS"
    ],
    "bills": [
        "['bil', 's']",
        "PLS"
    ],
    "billy": [
        "['bil', 'ee']",
        "PL"
    ],
    "bind": [
        "['bahynd']",
        "PNT"
    ],
    "bing": [
        "['bing']",
        "PNK"
    ],
    "binge": [
        "['binj']",
        "PNJ"
    ],
    "bingo": [
        "['bing', 'goh']",
        "PNK"
    ],
    "binoculars": [
        "['buh', 'nok', 'yuh', 'ler', 's']",
        "PNKLRS"
    ],
    "bio": [
        "['bahy', 'oh']",
        "P"
    ],
    "bionic": [
        "['bahy', 'on', 'ik']",
        "PNK"
    ],
    "bipolar": [
        "['bahy', 'poh', 'ler']",
        "PPLR"
    ],
    "bird": [
        "['burd']",
        "PRT"
    ],
    "birdie": [
        "['bur', 'dee']",
        "PRT"
    ],
    "birdies": [
        "['bur', 'dee', 's']",
        "PRTS"
    ],
    "birdman": [
        "['burd', 'man']",
        "PRTMN"
    ],
    "birds": [
        "['burd', 's']",
        "PRTS"
    ],
    "birkin": [
        [
            "burk",
            "in"
        ],
        "PRKN"
    ],
    "birmingham": [
        "[bur,ming,uhmfor1]",
        "PRMNKM"
    ],
    "birth": [
        "['burth']",
        "PR0"
    ],
    "birthday": [
        "['burth', 'dey']",
        "PR0T"
    ],
    "birthdays": [
        "[burth,dey,s]",
        "PR0TS"
    ],
    "birthed": [
        "[burth,ed]",
        "PR0T"
    ],
    "birthplace": [
        "[burth,pleys]",
        "PR0PLS"
    ],
    "birthright": [
        "[burth,rahyt]",
        "PR0RT"
    ],
    "bis": [
        "['bis']",
        "PS"
    ],
    "biscuit": [
        "['bis', 'kit']",
        "PSKT"
    ],
    "biscuits": [
        "[bis,kit,s]",
        "PSKTS"
    ],
    "bisexual": [
        "['bahy', 'sek', 'shoo', 'uhl']",
        "PSKSL"
    ],
    "bishop": [
        "['bish', 'uhp']",
        "PXP"
    ],
    "bit": [
        "['bit']",
        "PT"
    ],
    "bitch": [
        "['bich']",
        "PX"
    ],
    "bitched": [
        "['bich', 'ed']",
        "PXT"
    ],
    "bitches": [
        "['bich', 'es']",
        "PXS"
    ],
    "bitching": [
        "['bich', 'ing']",
        "PXNK"
    ],
    "bite": [
        "['bahyt']",
        "PT"
    ],
    "bites": [
        "['bahyt', 's']",
        "PTS"
    ],
    "biting": [
        "['bahy', 'ting']",
        "PTNK"
    ],
    "bits": [
        "[bit,s]",
        "PTS"
    ],
    "bitter": [
        "['bit', 'er']",
        "PTR"
    ],
    "bitty": [
        "['bit', 'ee']",
        "PT"
    ],
    "bity": [
        [
            "bit",
            "ee"
        ],
        "PT"
    ],
    "bizarre": [
        "[bih,zahr]",
        "PSR"
    ],
    "bk": [
        "['br', 'kl', 'm']",
        "PK"
    ],
    "black": [
        "['blak']",
        "PLK"
    ],
    "blackberry": [
        "['blak', 'ber', 'ee']",
        "PLKPR"
    ],
    "blacked": [
        "[blak,ed]",
        "PLKT"
    ],
    "blacker": [
        "[blak,er]",
        "PLKR"
    ],
    "blacking": [
        "['blak', 'ing']",
        "PLKNK"
    ],
    "blackjack": [
        "['blak', 'jak']",
        "PLKK"
    ],
    "blacks": [
        "[blak,s]",
        "PLKS"
    ],
    "bladder": [
        "['blad', 'er']",
        "PLTR"
    ],
    "blade": [
        "['bleyd']",
        "PLT"
    ],
    "blades": [
        "[bleyd,s]",
        "PLTS"
    ],
    "blah": [
        "['blah']",
        "PL"
    ],
    "blake": [
        "['bleyk']",
        "PLK"
    ],
    "blame": [
        "['bleym']",
        "PLM"
    ],
    "bland": [
        "[bland]",
        "PLNT"
    ],
    "blank": [
        "['blangk']",
        "PLNK"
    ],
    "blanket": [
        "['blang', 'kit']",
        "PLNKT"
    ],
    "blankets": [
        "[blang,kit,s]",
        "PLNKTS"
    ],
    "blanks": [
        "[blangk,s]",
        "PLNKS"
    ],
    "blast": [
        "['blast']",
        "PLST"
    ],
    "blasted": [
        "[blas,tid]",
        "PLSTT"
    ],
    "blasting": [
        "['blast', 'ing']",
        "PLSTNK"
    ],
    "blas\u00e9": [
        "['blah', 'zey']",
        "PLS"
    ],
    "blat": [
        "['blat']",
        "PLT"
    ],
    "blatant": [
        "[bleyt,nt]",
        "PLTNT"
    ],
    "blaze": [
        "['bleyz']",
        "PLS"
    ],
    "blazed": [
        "[bleyz,d]",
        "PLST"
    ],
    "blazer": [
        "['bley', 'zer']",
        "PLSR"
    ],
    "blazing": [
        "['bley', 'zing']",
        "PLSNK"
    ],
    "bleach": [
        "['bleech']",
        "PLX"
    ],
    "bleached": [
        "['bleech', 'ed']",
        "PLXT"
    ],
    "bleachers": [
        "['blee', 'cher', 's']",
        "PLXRS"
    ],
    "bleak": [
        "['bleek']",
        "PLK"
    ],
    "bleed": [
        "['bleed']",
        "PLT"
    ],
    "bleeding": [
        "['blee', 'ding']",
        "PLTNK"
    ],
    "bleeds": [
        "['bleed', 's']",
        "PLTS"
    ],
    "bleep": [
        "[bleep]",
        "PLP"
    ],
    "blemish": [
        "[blem,ish]",
        "PLMX"
    ],
    "blend": [
        "['blend']",
        "PLNT"
    ],
    "blender": [
        "['blen', 'der']",
        "PLNTR"
    ],
    "bless": [
        "['bles']",
        "PLS"
    ],
    "blessed": [
        "['bles', 'id']",
        "PLST"
    ],
    "blessing": [
        "['bles', 'ing']",
        "PLSNK"
    ],
    "blessings": [
        "['bles', 'ing', 's']",
        "PLSNKS"
    ],
    "blew": [
        "['bloo']",
        "PL"
    ],
    "blimp": [
        "['blimp']",
        "PLMP"
    ],
    "blind": [
        "['blahynd']",
        "PLNT"
    ],
    "blinded": [
        "[blahynd,ed]",
        "PLNTT"
    ],
    "blindfold": [
        "['blahynd', 'fohld']",
        "PLNTFLT"
    ],
    "blindfolded": [
        "[blahynd,fohld,ed]",
        "PLNTFLTT"
    ],
    "blinding": [
        "['blahyn', 'ding']",
        "PLNTNK"
    ],
    "blinds": [
        "['blahynd', 's']",
        "PLNTS"
    ],
    "blindside": [
        "[blahynd,sahyd]",
        "PLNTST"
    ],
    "bling": [
        "['blingorbling', 'bling']",
        "PLNK"
    ],
    "blinging": [
        "['blingorbling', 'bling', 'ing']",
        "PLNJNK"
    ],
    "blink": [
        "['blingk']",
        "PLNK"
    ],
    "blinkers": [
        "[bling,ker,s]",
        "PLNKRS"
    ],
    "blinking": [
        "['bling', 'king']",
        "PLNKNK"
    ],
    "bliss": [
        "[blis]",
        "PLS"
    ],
    "blisters": [
        "[blis,ter,s]",
        "PLSTRS"
    ],
    "blitz": [
        "['blits']",
        "PLTS"
    ],
    "blizzard": [
        "['bliz', 'erd']",
        "PLSRT"
    ],
    "blizzards": [
        "[bliz,erd,s]",
        "PLSRTS"
    ],
    "block": [
        "['blok']",
        "PLK"
    ],
    "block's": [
        "['blok', \"'s\"]",
        "PLKK"
    ],
    "blockbuster": [
        "['blok', 'buhs', 'ter']",
        "PLKPSTR"
    ],
    "blocked": [
        "['blok', 'ed']",
        "PLKT"
    ],
    "blockers": [
        "[blok,er,s]",
        "PLKRS"
    ],
    "blocking": [
        "['blok', 'ing']",
        "PLKNK"
    ],
    "blocks": [
        "['blok', 's']",
        "PLKS"
    ],
    "blog": [
        "['blawg']",
        "PLK"
    ],
    "bloggers": [
        "[blawg,gers]",
        "PLKRS"
    ],
    "blogging": [
        "[blawg,ging]",
        "PLJNK"
    ],
    "blogs": [
        "['blawg', 's']",
        "PLKS"
    ],
    "bloke": [
        "[blohk]",
        "PLK"
    ],
    "blond": [
        "[blond]",
        "PLNT"
    ],
    "blonde": [
        "['blond']",
        "PLNT"
    ],
    "blood": [
        "['bluhd']",
        "PLT"
    ],
    "blooded": [
        "['bluhd', 'id']",
        "PLTT"
    ],
    "bloodline": [
        "['bluhd', 'lahyn']",
        "PLTLN"
    ],
    "bloods": [
        "['bluhd', 's']",
        "PLTS"
    ],
    "bloodshot": [
        "[bluhd,shot]",
        "PLTXT"
    ],
    "bloodsuckers": [
        "[bluhd,suhk,er,s]",
        "PLTSKRS"
    ],
    "bloody": [
        "['bluhd', 'ee']",
        "PLT"
    ],
    "bloom": [
        "[bloom]",
        "PLM"
    ],
    "blouse": [
        "['blous']",
        "PLS"
    ],
    "blouses": [
        "[blous,s]",
        "PLSS"
    ],
    "blow": [
        "['bloh']",
        "PL"
    ],
    "blowed": [
        "['blohd']",
        "PLT"
    ],
    "blower": [
        "['bloh', 'er']",
        "PLR"
    ],
    "blowing": [
        "['bloh', 'ing']",
        "PLNK"
    ],
    "blown": [
        "['blohn']",
        "PLN"
    ],
    "blows": [
        "['bloh', 's']",
        "PLS"
    ],
    "blue": [
        "['bloo']",
        "PL"
    ],
    "blue's": [
        "[bloo,'s]",
        "PLS"
    ],
    "blueberry": [
        "[bloo,ber,ee]",
        "PLPR"
    ],
    "blueprint": [
        "['bloo', 'print']",
        "PLPRNT"
    ],
    "bluer": [
        "['bloo', 'r']",
        "PLR"
    ],
    "blues": [
        "['blooz']",
        "PLS"
    ],
    "bluff": [
        "['bluhf']",
        "PLF"
    ],
    "bluffing": [
        "['bluhf', 'ing']",
        "PLFNK"
    ],
    "blunt": [
        "['bluhnt']",
        "PLNT"
    ],
    "blunted": [
        "['bluhnt', 'ed']",
        "PLNTT"
    ],
    "blunts": [
        "['bluhnt', 's']",
        "PLNTS"
    ],
    "blur": [
        "['blur']",
        "PLR"
    ],
    "blurred": [
        "['blur', 'red']",
        "PLRT"
    ],
    "blurry": [
        "['blur', 'ee']",
        "PLR"
    ],
    "blush": [
        "['bluhsh']",
        "PLX"
    ],
    "blushing": [
        "[bluhsh,ing]",
        "PLXNK"
    ],
    "board": [
        "['bawrd']",
        "PRT"
    ],
    "boarded": [
        "['bawrd', 'ed']",
        "PRTT"
    ],
    "boards": [
        "['bawrd', 's']",
        "PRTS"
    ],
    "boast": [
        "['bohst']",
        "PST"
    ],
    "boasting": [
        "['bohst', 'ing']",
        "PSTNK"
    ],
    "boat": [
        "['boht']",
        "PT"
    ],
    "boatload": [
        "['boht', 'lohd']",
        "PTLT"
    ],
    "boats": [
        "['boht', 's']",
        "PTS"
    ],
    "bob": [
        "['bob']",
        "PP"
    ],
    "bobbing": [
        "[bob,ing]",
        "PPNK"
    ],
    "bobble": [
        "[bob,uhl]",
        "PPL"
    ],
    "bobby": [
        "['bob', 'ee']",
        "PP"
    ],
    "bodega": [
        "[boh,dey,guh]",
        "PTK"
    ],
    "bodied": [
        "['bod', 'eed']",
        "PTT"
    ],
    "body": [
        "['bod', 'ee']",
        "PT"
    ],
    "body's": [
        "['bod', 'ee', \"'s\"]",
        "PTS"
    ],
    "bodyguard": [
        "[bod,ee,gahrd]",
        "PTKRT"
    ],
    "bodyguards": [
        "[bod,ee,gahrd,s]",
        "PTKRTS"
    ],
    "bogart": [
        "['boh', 'gahrt']",
        "PKRT"
    ],
    "bogus": [
        "['boh', 'guhs']",
        "PKS"
    ],
    "boil": [
        "[boil]",
        "PL"
    ],
    "boiling": [
        "['boi', 'ling']",
        "PLNK"
    ],
    "boils": [
        "[boil,s]",
        "PLS"
    ],
    "bold": [
        "['bohld']",
        "PLT"
    ],
    "bolder": [
        "[bohld,er]",
        "PLTR"
    ],
    "bologna": [
        "['buh', 'loh', 'nee']",
        "PLN"
    ],
    "bolt": [
        "['bohlt']",
        "PLT"
    ],
    "bolts": [
        "[bohlt,s]",
        "PLTS"
    ],
    "bomb": [
        "['bom']",
        "PMP"
    ],
    "bombay": [
        "['bom', 'bey']",
        "PMP"
    ],
    "bomber": [
        "['bom', 'er']",
        "PMPR"
    ],
    "bombing": [
        "[bom,ing]",
        "PMPNK"
    ],
    "bombs": [
        "['bom', 's']",
        "PMPS"
    ],
    "bond": [
        "['bond']",
        "PNT"
    ],
    "bonds": [
        "['bond', 's']",
        "PNTS"
    ],
    "bone": [
        "['bohn']",
        "PN"
    ],
    "boned": [
        "['bohnd']",
        "PNT"
    ],
    "boner": [
        "['boh', 'ner']",
        "PNR"
    ],
    "bones": [
        "['bohn', 's']",
        "PNS"
    ],
    "bong": [
        "['bong']",
        "PNK"
    ],
    "bonita": [
        "['buh', 'nee', 'tuh']",
        "PNT"
    ],
    "bonkers": [
        "['bong', 'kerz']",
        "PNKRS"
    ],
    "bonnie": [
        "['bon', 'ee']",
        "PN"
    ],
    "bonny": [
        "[bon,ee]",
        "PN"
    ],
    "bonus": [
        "[boh,nuhs]",
        "PNS"
    ],
    "bony": [
        "[boh,nee]",
        "PN"
    ],
    "boo": [
        "['boo']",
        "P"
    ],
    "boobies": [
        [
            "boo",
            "bees"
        ],
        "PPS"
    ],
    "boobs": [
        "['boob', 's']",
        "PPS"
    ],
    "booby": [
        "['boo', 'bee']",
        "PP"
    ],
    "booed": [
        "[boo,ed]",
        "PT"
    ],
    "booger": [
        "['boog', 'er']",
        "PKR"
    ],
    "boogers": [
        "['boog', 'er', 's']",
        "PKRS"
    ],
    "boogie": [
        "['boog', 'ee']",
        "PJ"
    ],
    "book": [
        "['book']",
        "PK"
    ],
    "booked": [
        "['book', 'ed']",
        "PKT"
    ],
    "booker": [
        "['book', 'er']",
        "PKR"
    ],
    "booking": [
        "['book', 'ing']",
        "PKNK"
    ],
    "books": [
        "['book', 's']",
        "PKS"
    ],
    "boom": [
        "['boom']",
        "PM"
    ],
    "boomerang": [
        "['boo', 'muh', 'rang']",
        "PMRNK"
    ],
    "booming": [
        "['boom', 'ing']",
        "PMNK"
    ],
    "booms": [
        "[boom,s]",
        "PMS"
    ],
    "boost": [
        "['boost']",
        "PST"
    ],
    "booster": [
        "[boo,ster]",
        "PSTR"
    ],
    "boosters": [
        "['boo', 'ster', 's']",
        "PSTRS"
    ],
    "boosting": [
        "['boost', 'ing']",
        "PSTNK"
    ],
    "boot": [
        "['boot']",
        "PT"
    ],
    "booted": [
        "['boo', 'tid']",
        "PTT"
    ],
    "booth": [
        "['booth']",
        "P0"
    ],
    "bootie": [
        "[boo,tee]",
        "PT"
    ],
    "booties": [
        "['boo', 'tee', 's']",
        "PTS"
    ],
    "bootleg": [
        "[boot,leg]",
        "PTLK"
    ],
    "boots": [
        "['boots']",
        "PTS"
    ],
    "booty": [
        "['boo', 'tee']",
        "PT"
    ],
    "booze": [
        "['booz']",
        "PS"
    ],
    "boozy": [
        "['boo', 'zee']",
        "PS"
    ],
    "bop": [
        "['bop']",
        "PP"
    ],
    "bopping": [
        "['bop', 'ping']",
        "PPNK"
    ],
    "bops": [
        "['bop', 's']",
        "PPS"
    ],
    "bora": [
        "[bawr,uh]",
        "PR"
    ],
    "border": [
        "['bawr', 'der']",
        "PRTR"
    ],
    "borderline": [
        "['bawr', 'der', 'lahyn']",
        "PRTRLN"
    ],
    "borders": [
        "[bawr,derz]",
        "PRTRS"
    ],
    "bore": [
        "['bawr']",
        "PR"
    ],
    "bored": [
        "['bawr', 'd']",
        "PRT"
    ],
    "boredom": [
        "[bawr,duhm]",
        "PRTM"
    ],
    "boring": [
        "['bawr', 'ing']",
        "PRNK"
    ],
    "born": [
        "['bawrn']",
        "PRN"
    ],
    "borough": [
        "['bur', 'oh']",
        "PRF"
    ],
    "borrow": [
        "['bor', 'oh']",
        "PR"
    ],
    "borrowed": [
        "[bor,oh,ed]",
        "PRT"
    ],
    "boss": [
        "['baws']",
        "PS"
    ],
    "bossed": [
        "['baws', 'ed']",
        "PST"
    ],
    "bosses": [
        "['baws', 'es']",
        "PSS"
    ],
    "bossing": [
        "[baws,ing]",
        "PSNK"
    ],
    "bossy": [
        "[baw,see]",
        "PS"
    ],
    "boston": [
        "['baw', 'stuhn']",
        "PSTN"
    ],
    "both": [
        "['bohth']",
        "P0"
    ],
    "bother": [
        "['both', 'er']",
        "P0R"
    ],
    "bothered": [
        "['both', 'er', 'ed']",
        "P0RT"
    ],
    "bothering": [
        "['both', 'er', 'ing']",
        "P0RNK"
    ],
    "bothers": [
        "[both,er,s]",
        "P0RS"
    ],
    "bottle": [
        "['bot', 'l']",
        "PTL"
    ],
    "bottled": [
        "[bot,l,d]",
        "PTLT"
    ],
    "bottles": [
        "['bot', 'l', 's']",
        "PTLS"
    ],
    "bottom": [
        "['bot', 'uhm']",
        "PTM"
    ],
    "bottoms": [
        "['bot', 'uhm', 's']",
        "PTMS"
    ],
    "bought": [
        "['bawt']",
        "PT"
    ],
    "bougie": [
        "['boo', 'jee']",
        "PJ"
    ],
    "boulder": [
        "['bohl', 'der']",
        "PLTR"
    ],
    "boulders": [
        "['bohl', 'der', 's']",
        "PLTRS"
    ],
    "boulevard": [
        "['bool', 'uh', 'vahrd']",
        "PLFRT"
    ],
    "bounce": [
        "['bouns']",
        "PNS"
    ],
    "bounced": [
        "['bouns', 'd']",
        "PNST"
    ],
    "bouncer": [
        "['boun', 'ser']",
        "PNSR"
    ],
    "bouncers": [
        "['boun', 'ser', 's']",
        "PNSRS"
    ],
    "bouncing": [
        "['boun', 'sing']",
        "PNSNK"
    ],
    "bound": [
        "['bound']",
        "PNT"
    ],
    "bounds": [
        "[bound,s]",
        "PNTS"
    ],
    "bounty": [
        "['boun', 'tee']",
        "PNT"
    ],
    "bouquet": [
        "['boh', 'key']",
        "PKT"
    ],
    "bourbon": [
        "['boor', 'buhn']",
        "PRPN"
    ],
    "bout": [
        "['bout']",
        "PT"
    ],
    "bow": [
        "['bou']",
        "P"
    ],
    "bowed": [
        "[bou,ed]",
        "PT"
    ],
    "bowels": [
        "['bou', 'uhl', 's']",
        "PLS"
    ],
    "bowie": [
        "[boh,ee]",
        "P"
    ],
    "bowl": [
        "['bohl']",
        "PL"
    ],
    "bowling": [
        "['boh', 'ling']",
        "PLNK"
    ],
    "bowls": [
        "['bohl', 's']",
        "PLS"
    ],
    "bows": [
        "['bou', 's']",
        "PS"
    ],
    "bowtie": [
        [
            "bou",
            "tahy"
        ],
        "PT"
    ],
    "box": [
        "['boks']",
        "PKS"
    ],
    "boxed": [
        "[boks,ed]",
        "PKST"
    ],
    "boxer": [
        "[bok,ser]",
        "PKSR"
    ],
    "boxers": [
        "['bok', 'ser', 's']",
        "PKSRS"
    ],
    "boxes": [
        "['boks', 'es']",
        "PKSS"
    ],
    "boxing": [
        "['bok', 'sing']",
        "PKSNK"
    ],
    "boy": [
        "['boi']",
        "P"
    ],
    "boy's": [
        "['boi', \"'s\"]",
        "PS"
    ],
    "boyfriend": [
        "['boi', 'frend']",
        "PFRNT"
    ],
    "boyfriend's": [
        "[boi,frend,'s]",
        "PFRNTTS"
    ],
    "boyfriends": [
        "['boi', 'frend', 's']",
        "PFRNTS"
    ],
    "boys": [
        "['boi', 's']",
        "PS"
    ],
    "bozo": [
        "[boh,zoh]",
        "PS"
    ],
    "bra": [
        "['brah']",
        "PR"
    ],
    "brace": [
        "[breys]",
        "PRS"
    ],
    "bracelet": [
        "['breys', 'lit']",
        "PRSLT"
    ],
    "bracelets": [
        "['breys', 'lit', 's']",
        "PRSLTS"
    ],
    "braces": [
        "['breys', 's']",
        "PRSS"
    ],
    "bracket": [
        "['brak', 'it']",
        "PRKT"
    ],
    "brad": [
        "['brad']",
        "PRT"
    ],
    "brady": [
        "['brey', 'dee']",
        "PRT"
    ],
    "brag": [
        "['brag']",
        "PRK"
    ],
    "bragging": [
        "['brag', 'ging']",
        "PRJNK"
    ],
    "braging": [
        [
            "brag",
            "ing"
        ],
        "PRJNK"
    ],
    "braid": [
        "[breyd]",
        "PRT"
    ],
    "braided": [
        "[breyd,ed]",
        "PRTT"
    ],
    "braids": [
        "['breyd', 's']",
        "PRTS"
    ],
    "braille": [
        "[breyl]",
        "PRL"
    ],
    "brain": [
        "['breyn']",
        "PRN"
    ],
    "brain's": [
        "[breyn,'s]",
        "PRNNS"
    ],
    "brained": [
        "[breynd]",
        "PRNT"
    ],
    "brainless": [
        "[breyn,lis]",
        "PRNLS"
    ],
    "brains": [
        "['breyn', 's']",
        "PRNS"
    ],
    "brainstorm": [
        "[breyn,stawrm]",
        "PRNSTRM"
    ],
    "brainwash": [
        "['breyn', 'wosh']",
        "PRNX"
    ],
    "brainwashed": [
        "['breyn', 'wosh', 'ed']",
        "PRNXT"
    ],
    "braise": [
        "['breyz']",
        "PRS"
    ],
    "brake": [
        "['breyk']",
        "PRK"
    ],
    "brakes": [
        "['breyk', 's']",
        "PRKS"
    ],
    "branch": [
        "[branch]",
        "PRNX"
    ],
    "branches": [
        "[branch,es]",
        "PRNXS"
    ],
    "brand": [
        "['brand']",
        "PRNT"
    ],
    "brands": [
        "['brand', 's']",
        "PRNTS"
    ],
    "brandy": [
        "[bran,dee]",
        "PRNT"
    ],
    "bras": [
        "['brah', 's']",
        "PRS"
    ],
    "brash": [
        "[brash]",
        "PRX"
    ],
    "brass": [
        "[bras]",
        "PRS"
    ],
    "brat": [
        "['brat']",
        "PRT"
    ],
    "brave": [
        "['breyv']",
        "PRF"
    ],
    "braves": [
        "[breyv,s]",
        "PRFS"
    ],
    "bravo": [
        "[brah,voh]",
        "PRF"
    ],
    "brawl": [
        "[brawl]",
        "PRL"
    ],
    "brawling": [
        "[brawl,ing]",
        "PRLNK"
    ],
    "brazil": [
        "[bruh,zil]",
        "PRSL"
    ],
    "brazilian": [
        "[bruh,zil,]",
        "PRSLN"
    ],
    "bread": [
        "['bred']",
        "PRT"
    ],
    "breads": [
        "[bred,s]",
        "PRTS"
    ],
    "break": [
        "['breyk']",
        "PRK"
    ],
    "break's": [
        "[breyk,'s]",
        "PRKKS"
    ],
    "breakdown": [
        "['breyk', 'doun']",
        "PRKTN"
    ],
    "breaker": [
        "[brey,ker]",
        "PRKR"
    ],
    "breakfast": [
        "['brek', 'fuhst']",
        "PRKFST"
    ],
    "breaking": [
        "['brey', 'king']",
        "PRKNK"
    ],
    "breaks": [
        "[breyk,s]",
        "PRKS"
    ],
    "breast": [
        "['brest']",
        "PRST"
    ],
    "breasts": [
        "['brest', 's']",
        "PRSTS"
    ],
    "breath": [
        "['breth']",
        "PR0"
    ],
    "breathe": [
        "['breeth']",
        "PR0"
    ],
    "breather": [
        "[bree,ther]",
        "PR0R"
    ],
    "breathing": [
        "['bree', 'thing']",
        "PR0NK"
    ],
    "bred": [
        "['bred']",
        "PRT"
    ],
    "breed": [
        "['breed']",
        "PRT"
    ],
    "breeds": [
        "[breed,s]",
        "PRTS"
    ],
    "breeze": [
        "['breez']",
        "PRS"
    ],
    "breezes": [
        "[breez,s]",
        "PRSS"
    ],
    "breezy": [
        "['bree', 'zee']",
        "PRS"
    ],
    "brethren": [
        "[breth,rin]",
        "PR0RN"
    ],
    "brew": [
        "['broo']",
        "PR"
    ],
    "brewing": [
        "[broo,ing]",
        "PRNK"
    ],
    "brews": [
        "[broo,s]",
        "PRS"
    ],
    "brian": [
        "['brahy', 'uhn']",
        "PRN"
    ],
    "brick": [
        "['brik']",
        "PRK"
    ],
    "bricks": [
        "['brik', 's']",
        "PRKS"
    ],
    "bride": [
        "['brahyd']",
        "PRT"
    ],
    "bride's": [
        "[brahyd,'s]",
        "PRTS"
    ],
    "bridge": [
        "['brij']",
        "PRJ"
    ],
    "bridges": [
        "[brij,iz]",
        "PRJS"
    ],
    "brief": [
        "['breef']",
        "PRF"
    ],
    "briefcase": [
        "[breef,keys]",
        "PRFKS"
    ],
    "bright": [
        "['brahyt']",
        "PRT"
    ],
    "brighten": [
        "[brahyt,n]",
        "PRTN"
    ],
    "brighter": [
        "['brahyt', 'er']",
        "PRTR"
    ],
    "brightest": [
        "['brahyt', 'est']",
        "PRTST"
    ],
    "brilliant": [
        "[bril,yuhnt]",
        "PRLNT"
    ],
    "brim": [
        "[brim]",
        "PRM"
    ],
    "bring": [
        "['bring']",
        "PRNK"
    ],
    "bringing": [
        "['bring', 'ing']",
        "PRNJNK"
    ],
    "brings": [
        "['bring', 's']",
        "PRNKS"
    ],
    "brink": [
        "[bringk]",
        "PRNK"
    ],
    "brinks": [
        "['bringk', 's']",
        "PRNKS"
    ],
    "brisk": [
        "['brisk']",
        "PRSK"
    ],
    "britches": [
        "['brich', 'iz']",
        "PRXS"
    ],
    "british": [
        "[brit,ish]",
        "PRTX"
    ],
    "britney": [
        [
            "brit",
            "ney"
        ],
        "PRTN"
    ],
    "brittany": [
        "['brit', 'n', 'ee']",
        "PRTN"
    ],
    "bro": [
        "['broh']",
        "PR"
    ],
    "broad": [
        "['brawd']",
        "PRT"
    ],
    "broadcast": [
        "[brawd,kast]",
        "PRTKST"
    ],
    "broads": [
        "['brawdz']",
        "PRTS"
    ],
    "broadway": [
        "[brawd,wey]",
        "PRT"
    ],
    "broccoli": [
        "['brok', 'uh', 'lee']",
        "PRKL"
    ],
    "brody": [
        [
            "broh",
            "dee"
        ],
        "PRT"
    ],
    "broke": [
        "['brohk']",
        "PRK"
    ],
    "broken": [
        "['broh', 'kuhn']",
        "PRKN"
    ],
    "broker": [
        "[broh,ker]",
        "PRKR"
    ],
    "brome": [
        "[brohm,gras,]",
        "PRM"
    ],
    "bronco": [
        "['brong', 'koh']",
        "PRNK"
    ],
    "broncos": [
        "[brong,koh,s]",
        "PRNKS"
    ],
    "bronx": [
        "['brongks']",
        "PRNKS"
    ],
    "bronze": [
        "['bronz']",
        "PRNS"
    ],
    "brook": [
        "[brook]",
        "PRK"
    ],
    "brooklyn": [
        "['brook', 'lin']",
        "PRKLN"
    ],
    "broom": [
        "['broom']",
        "PRM"
    ],
    "bros": [
        "['broh', 's']",
        "PRS"
    ],
    "brother": [
        "['bruhth', 'erorfor9']",
        "PR0R"
    ],
    "brother's": [
        "['bruhth', 'erorfor9', \"'s\"]",
        "PR0RRS"
    ],
    "brothers": [
        "['bruhth', 'erorfor9', 's']",
        "PR0RS"
    ],
    "brought": [
        "['brawt']",
        "PRT"
    ],
    "brow": [
        "[brou]",
        "PR"
    ],
    "brown": [
        "['broun']",
        "PRN"
    ],
    "brown's": [
        "['broun', \"'s\"]",
        "PRNNS"
    ],
    "browns": [
        "['broun', 's']",
        "PRNS"
    ],
    "brownsville": [
        "[brounz,vil]",
        "PRNSFL"
    ],
    "brr": [
        "['bur']",
        "PR"
    ],
    "bruce": [
        "['broos']",
        "PRS"
    ],
    "bruins": [
        "['broo', 'in', 's']",
        "PRNS"
    ],
    "bruise": [
        "['brooz']",
        "PRS"
    ],
    "bruised": [
        "['brooz', 'd']",
        "PRST"
    ],
    "bruises": [
        "[brooz,s]",
        "PRSS"
    ],
    "brunch": [
        "['bruhnch']",
        "PRNX"
    ],
    "brunette": [
        "['broo', 'net']",
        "PRNT"
    ],
    "brung": [
        "['bruhng']",
        "PRNK"
    ],
    "bruno": [
        "[broo,noh]",
        "PRN"
    ],
    "brush": [
        "['bruhsh']",
        "PRX"
    ],
    "brushes": [
        "[bruhsh,es]",
        "PRXS"
    ],
    "brushing": [
        "['bruhsh', 'ing']",
        "PRXNK"
    ],
    "brutal": [
        "[broot,l]",
        "PRTL"
    ],
    "bryan": [
        "[brahy,uhn]",
        "PRN"
    ],
    "bs": [
        "['bee']",
        "PS"
    ],
    "bubba": [
        "['buhb', 'uh']",
        "PP"
    ],
    "bubble": [
        "['buhb', 'uhl']",
        "PPL"
    ],
    "bubbles": [
        "[buhb,uhl,s]",
        "PPLS"
    ],
    "bubbly": [
        "['buhb', 'lee']",
        "PPL"
    ],
    "buck": [
        "['buhk']",
        "PK"
    ],
    "bucked": [
        "[buhkt]",
        "PKT"
    ],
    "bucket": [
        "['buhk', 'it']",
        "PKT"
    ],
    "buckets": [
        "[buhk,it,s]",
        "PKTS"
    ],
    "bucking": [
        "[buhk,ing]",
        "PKNK"
    ],
    "buckle": [
        "['buhk', 'uhl']",
        "PKL"
    ],
    "bucks": [
        "['buhks']",
        "PKS"
    ],
    "bud": [
        "['buhd']",
        "PT"
    ],
    "buddha": [
        "['boo', 'duh']",
        "PT"
    ],
    "buddies": [
        [
            "buhd",
            "ees"
        ],
        "PTS"
    ],
    "buddy": [
        "['buhd', 'ee']",
        "PT"
    ],
    "budge": [
        "['buhj']",
        "PJ"
    ],
    "budget": [
        "['buhj', 'it']",
        "PJT"
    ],
    "buds": [
        "['buhd', 's']",
        "PTS"
    ],
    "buff": [
        "['buhf']",
        "PF"
    ],
    "buffer": [
        "[buhf,er]",
        "PFR"
    ],
    "bug": [
        "[buhg]",
        "PK"
    ],
    "bugging": [
        "[buhg,ging]",
        "PKNK"
    ],
    "bugs": [
        "[buhgz]",
        "PKS"
    ],
    "build": [
        "['bild']",
        "PLT"
    ],
    "builder": [
        "['bil', 'der']",
        "PLTR"
    ],
    "building": [
        "['bil', 'ding']",
        "PLTNK"
    ],
    "buildings": [
        "['bil', 'ding', 's']",
        "PLTNKS"
    ],
    "built": [
        "['bilt']",
        "PLT"
    ],
    "bulbs": [
        "[buhlb,s]",
        "PLPS"
    ],
    "bulimic": [
        "[byoo,lim,ik]",
        "PLMK"
    ],
    "bull": [
        "['bool']",
        "PL"
    ],
    "bulldog": [
        "['bool', 'dawg']",
        "PLTK"
    ],
    "bullet": [
        "['bool', 'it']",
        "PLT"
    ],
    "bulletproof": [
        "['bool', 'it', 'proof']",
        "PLTPRF"
    ],
    "bullets": [
        "['bool', 'it', 's']",
        "PLTS"
    ],
    "bulls": [
        "[bool,s]",
        "PLS"
    ],
    "bullshit": [
        "['bool', 'shit']",
        "PLXT"
    ],
    "bullshitting": [
        "[bool,shit,ting]",
        "PLXTNK"
    ],
    "bully": [
        "['bool', 'ee']",
        "PL"
    ],
    "bum": [
        "['buhm']",
        "PM"
    ],
    "bumble": [
        "['buhm', 'buhl']",
        "PMPL"
    ],
    "bumblebee": [
        "['buhm', 'buhl', 'bee']",
        "PMPLP"
    ],
    "bummer": [
        "['buhm', 'er']",
        "PMR"
    ],
    "bumming": [
        "[buhm,ming]",
        "PMNK"
    ],
    "bump": [
        "['buhmp']",
        "PMP"
    ],
    "bumped": [
        "['buhmp', 'ed']",
        "PMPT"
    ],
    "bumper": [
        "[buhm,per]",
        "PMPR"
    ],
    "bumping": [
        "['buhmp', 'ing']",
        "PMPNK"
    ],
    "bumps": [
        "['buhmp', 's']",
        "PMPS"
    ],
    "bums": [
        "['buhm', 's']",
        "PMS"
    ],
    "bun": [
        "['buhn']",
        "PN"
    ],
    "bunch": [
        "['buhnch']",
        "PNX"
    ],
    "bundle": [
        "['buhn', 'dl']",
        "PNTL"
    ],
    "bundles": [
        "['buhn', 'dl', 's']",
        "PNTLS"
    ],
    "bungee": [
        "['buhn', 'jee']",
        "PNJ"
    ],
    "bunk": [
        "['buhngk']",
        "PNK"
    ],
    "bunking": [
        "['buhngk', 'ing']",
        "PNKNK"
    ],
    "bunny": [
        "['buhn', 'ee']",
        "PN"
    ],
    "buns": [
        "['buhn', 's']",
        "PNS"
    ],
    "bur": [
        "['bur']",
        "PR"
    ],
    "burberry": [
        "['bur', 'buh', 'ree']",
        "PRPR"
    ],
    "burden": [
        "[bur,dn]",
        "PRTN"
    ],
    "burdens": [
        "['bur', 'dn', 's']",
        "PRTNS"
    ],
    "burger": [
        "['bur', 'ger']",
        "PRKR"
    ],
    "burgers": [
        "['bur', 'ger', 's']",
        "PRKRS"
    ],
    "burglar": [
        "['bur', 'gler']",
        "PRKLR"
    ],
    "burglary": [
        "['bur', 'gluh', 'ree']",
        "PRKLR"
    ],
    "burgundy": [
        "[bur,guhn,dee]",
        "PRKNT"
    ],
    "burial": [
        "[ber,ee,uhl]",
        "PRL"
    ],
    "burn": [
        "['burn']",
        "PRN"
    ],
    "burned": [
        "[burn,ed]",
        "PRNT"
    ],
    "burner": [
        "['bur', 'ner']",
        "PRNR"
    ],
    "burners": [
        "['bur', 'ner', 's']",
        "PRNRS"
    ],
    "burning": [
        "['bur', 'ning']",
        "PRNNK"
    ],
    "burns": [
        "[burnz]",
        "PRNS"
    ],
    "burnt": [
        "['burnt']",
        "PRNT"
    ],
    "burp": [
        "['burp']",
        "PRP"
    ],
    "burping": [
        "['burp', 'ing']",
        "PRPNK"
    ],
    "burr": [
        "['bur']",
        "PR"
    ],
    "burst": [
        "[burst]",
        "PRST"
    ],
    "bury": [
        "['ber', 'ee']",
        "PR"
    ],
    "burying": [
        "[ber,ee,ing]",
        "PRNK"
    ],
    "bus": [
        "['buhs']",
        "PS"
    ],
    "buses": [
        "['buhs', 'es']",
        "PSS"
    ],
    "bush": [
        "['boosh']",
        "PX"
    ],
    "bushes": [
        "['boosh', 'es']",
        "PXS"
    ],
    "business": [
        "['biz', 'nis']",
        "PSNS"
    ],
    "businessman": [
        "['biz', 'nis', 'man']",
        "PSNSMN"
    ],
    "buss": [
        "[buhs]",
        "PS"
    ],
    "bussing": [
        "['buhs', 'sing']",
        "PSNK"
    ],
    "bust": [
        "['buhst']",
        "PST"
    ],
    "busted": [
        "['buhst', 'ed']",
        "PSTT"
    ],
    "buster": [
        "[buhs,ter]",
        "PSTR"
    ],
    "busters": [
        "['buhs', 'ter', 's']",
        "PSTRS"
    ],
    "busting": [
        "['buhst', 'ing']",
        "PSTNK"
    ],
    "busty": [
        "['buhs', 'tee']",
        "PST"
    ],
    "busy": [
        "['biz', 'ee']",
        "PS"
    ],
    "but": [
        "['buht']",
        "PT"
    ],
    "butcher": [
        "['booch', 'er']",
        "PXR"
    ],
    "butler": [
        "[buht,ler]",
        "PTLR"
    ],
    "butt": [
        "['buht']",
        "PT"
    ],
    "butter": [
        "['buht', 'er']",
        "PTR"
    ],
    "buttercup": [
        "[buht,er,kuhp]",
        "PTRKP"
    ],
    "buttercups": [
        "[buht,er,kuhp,s]",
        "PTRKPS"
    ],
    "butterfly": [
        "['buht', 'er', 'flahy']",
        "PTRFL"
    ],
    "butters": [
        "[buht,er,s]",
        "PTRS"
    ],
    "button": [
        "['buht', 'n']",
        "PTN"
    ],
    "buttoned": [
        "[buht,n,ed]",
        "PTNT"
    ],
    "buttons": [
        "['buht', 'nz']",
        "PTNS"
    ],
    "butts": [
        "[buht,s]",
        "PTS"
    ],
    "buy": [
        "['bahy']",
        "P"
    ],
    "buyer": [
        "['bahy', 'er']",
        "PR"
    ],
    "buyers": [
        "[bahy,er,s]",
        "PRS"
    ],
    "buying": [
        "['bahy', 'ing']",
        "PNK"
    ],
    "buys": [
        "[bahy,s]",
        "PS"
    ],
    "buzz": [
        "['buhz']",
        "PS"
    ],
    "buzzing": [
        "['buhz', 'ing']",
        "PSNK"
    ],
    "by": [
        "['bahy']",
        "P"
    ],
    "by's": [
        "['bahy', \"'s\"]",
        "PS"
    ],
    "bye": [
        "['bahy']",
        "P"
    ],
    "bygones": [
        "[bahy,gawn,s]",
        "PKNS"
    ],
    "c": [
        "['see', '']",
        "K"
    ],
    "c'mon": [
        "['kmon']",
        "KKMN"
    ],
    "ca": [
        "['kah']",
        "K"
    ],
    "cab": [
        "['kab']",
        "KP"
    ],
    "cabana": [
        "[kuh,ban,uh]",
        "KPN"
    ],
    "cabanas": [
        "[kuh,ban,uh,s]",
        "KPNS"
    ],
    "cabbage": [
        "['kab', 'ij']",
        "KPJ"
    ],
    "cabinet": [
        "[kab,uh,nit]",
        "KPNT"
    ],
    "cabinets": [
        "[kab,uh,nit,s]",
        "KPNTS"
    ],
    "cabing": [
        [
            "kah",
            "bing"
        ],
        "KPNK"
    ],
    "cable": [
        "['key', 'buhl']",
        "KPL"
    ],
    "cabs": [
        "[kab,s]",
        "KPS"
    ],
    "cactus": [
        "['kak', 'tuhs']",
        "KKTS"
    ],
    "cadastre": [
        "[kuh,das,ter]",
        "KTSTR"
    ],
    "caddy": [
        "['kad', 'ee']",
        "KT"
    ],
    "cadence": [
        "['keyd', 'ns']",
        "KTNS"
    ],
    "cadillac": [
        "['kad', 'l', 'ak']",
        "KTLK"
    ],
    "cadillacs": [
        "['kad', 'l', 'ak', 's']",
        "KTLKS"
    ],
    "caesar": [
        "['see', 'zer']",
        "SSR"
    ],
    "caesar's": [
        "['see', 'zer', \"'s\"]",
        "SSRRS"
    ],
    "cage": [
        "['keyj']",
        "KJ"
    ],
    "caged": [
        "['keyj', 'd']",
        "KJT"
    ],
    "cages": [
        "['keyj', 's']",
        "KJS"
    ],
    "cahoots": [
        "[kuh,hoot,s]",
        "KHTS"
    ],
    "cain": [
        "['keyn']",
        "KN"
    ],
    "caine": [
        "['keyn']",
        "KN"
    ],
    "cajun": [
        "['key', 'juhn']",
        "KJN"
    ],
    "cake": [
        "['keyk']",
        "KK"
    ],
    "cakes": [
        "['keyk', 's']",
        "KKS"
    ],
    "cal": [
        "['kal']",
        "KL"
    ],
    "calamari": [
        "['kal', 'uh', 'mahr', 'ee']",
        "KLMR"
    ],
    "calculated": [
        "[kal,kyuh,ley,tid]",
        "KLKLTT"
    ],
    "calculating": [
        "[kal,kyuh,ley,ting]",
        "KLKLTNK"
    ],
    "calculator": [
        "['kal', 'kyuh', 'ley', 'ter']",
        "KLKLTR"
    ],
    "calendar": [
        "['kal', 'uhn', 'der']",
        "KLNTR"
    ],
    "calendars": [
        "[kal,uhn,der,s]",
        "KLNTRS"
    ],
    "calender": [
        "[kal,uhn,der]",
        "KLNTR"
    ],
    "cali": [
        "['kah', 'lee']",
        "KL"
    ],
    "cali's": [
        "[kah,lee,'s]",
        "KLS"
    ],
    "caliber": [
        "['kal', 'uh', 'ber']",
        "KLPR"
    ],
    "calico": [
        "[kal,i,koh]",
        "KLK"
    ],
    "california": [
        "['kal', 'uh', 'fawrn', 'yuh']",
        "KLFRN"
    ],
    "call": [
        "['kawl']",
        "KL"
    ],
    "called": [
        "['kawl', 'ed']",
        "KLT"
    ],
    "caller": [
        "['kaw', 'ler']",
        "KLR"
    ],
    "calling": [
        "['kaw', 'ling']",
        "KLNK"
    ],
    "callous": [
        "[kal,uhs]",
        "KLS"
    ],
    "calls": [
        "['kawl', 's']",
        "KLS"
    ],
    "calm": [
        "['kahm']",
        "KLM"
    ],
    "calories": [
        "[kal,uh,ree,s]",
        "KLRS"
    ],
    "cam": [
        "['kam']",
        "KM"
    ],
    "cam'ron": [
        [
            "kam",
            "er",
            "uhn"
        ],
        "KMMRN"
    ],
    "came": [
        "['keym']",
        "KM"
    ],
    "camel": [
        "['kam', 'uhl']",
        "KML"
    ],
    "camels": [
        "['kam', 'uhl', 's']",
        "KMLS"
    ],
    "camera": [
        "['kam', 'er', 'uh']",
        "KMR"
    ],
    "camera's": [
        "[kam,er,uh,'s]",
        "KMRS"
    ],
    "cameraman": [
        "[kam,er,uh,man]",
        "KMRMN"
    ],
    "cameras": [
        "['kam', 'er', 'uh', 's']",
        "KMRS"
    ],
    "camo": [
        "['kam', 'oh']",
        "KM"
    ],
    "camouflage": [
        "['kam', 'uh', 'flahzh']",
        "KMFLJ"
    ],
    "camp": [
        "['kamp']",
        "KMP"
    ],
    "campaign": [
        "['kam', 'peyn']",
        "KMPN"
    ],
    "campbell": [
        "[kam,buhl]",
        "KMPL"
    ],
    "campbell's": [
        "[kam,buhl,'s]",
        "KMPLL"
    ],
    "campfire": [
        "[kamp,fahyuhr]",
        "KMPFR"
    ],
    "campus": [
        "['kam', 'puhs']",
        "KMPS"
    ],
    "campuses": [
        "[kam,puhs,es]",
        "KMPSS"
    ],
    "can": [
        "['kan']",
        "KN"
    ],
    "can't": [
        "['kant']",
        "KNNT"
    ],
    "canal": [
        "['kuh', 'nal']",
        "KNL"
    ],
    "canary": [
        "['kuh', 'nair', 'ee']",
        "KNR"
    ],
    "cancel": [
        "['kan', 'suhl']",
        "KNSL"
    ],
    "cancelled": [
        "['kan', 'suhl', 'led']",
        "KNSLT"
    ],
    "cancer": [
        "['kan', 'ser']",
        "KNSR"
    ],
    "candidate": [
        "[nounkan,di,deyt]",
        "KNTTT"
    ],
    "candidates": [
        "[nounkan,di,deyt,s]",
        "KNTTTS"
    ],
    "candies": [
        [
            "kan",
            "dahyz"
        ],
        "KNTS"
    ],
    "candle": [
        "['kan', 'dl']",
        "KNTL"
    ],
    "candlelight": [
        "[kan,dl,lahyt]",
        "KNTLLT"
    ],
    "candles": [
        "['kan', 'dl', 's']",
        "KNTLS"
    ],
    "candy": [
        "['kan', 'dee']",
        "KNT"
    ],
    "cane": [
        "['keyn']",
        "KN"
    ],
    "canines": [
        "[key,nahyn,s]",
        "KNNS"
    ],
    "cannabis": [
        "[kan,uh,bis]",
        "KNPS"
    ],
    "canned": [
        "[kand]",
        "KNT"
    ],
    "cannibal": [
        "['kan', 'uh', 'buhl']",
        "KNPL"
    ],
    "cannon": [
        "[kan,uhn]",
        "KNN"
    ],
    "cannons": [
        "[kan,uhn,s]",
        "KNNS"
    ],
    "cannot": [
        "['kan', 'ot']",
        "KNT"
    ],
    "canopy": [
        "[kan,uh,pee]",
        "KNP"
    ],
    "cans": [
        "['kan', 's']",
        "KNS"
    ],
    "cant": [
        "['kant']",
        "KNT"
    ],
    "cantaloupe": [
        "['kan', 'tl', 'ohp']",
        "KNTLP"
    ],
    "canvas": [
        "['kan', 'vuhs']",
        "KNFS"
    ],
    "canyon": [
        "[kan,yuhn]",
        "KNN"
    ],
    "cap": [
        "['kap']",
        "KP"
    ],
    "capacity": [
        "[kuh,pas,i,tee]",
        "KPST"
    ],
    "cape": [
        "['keyp']",
        "KP"
    ],
    "caper": [
        "[key,per]",
        "KPR"
    ],
    "capers": [
        "['key', 'per', 's']",
        "KPRS"
    ],
    "capital": [
        "['kap', 'i', 'tl']",
        "KPTL"
    ],
    "capitol": [
        "[kap,i,tl]",
        "KPTL"
    ],
    "capo": [
        "['key', 'poh']",
        "KP"
    ],
    "capone": [
        "['kuh', 'pohn']",
        "KPN"
    ],
    "capped": [
        "['kap', 'ped']",
        "KPT"
    ],
    "capping": [
        "['kap', 'ing']",
        "KPNK"
    ],
    "capri": [
        "[kah,pree]",
        "KPR"
    ],
    "caprice": [
        "[kuh,prees]",
        "KPRS"
    ],
    "caprices": [
        "[kuh,prees,s]",
        "KPRSS"
    ],
    "caps": [
        "['kap', 's']",
        "KPS"
    ],
    "capsule": [
        "[kap,suhl]",
        "KPSL"
    ],
    "captain": [
        "['kap', 'tuhn']",
        "KPTN"
    ],
    "caption": [
        "['kap', 'shuhn']",
        "KPXN"
    ],
    "captive": [
        "[kap,tiv]",
        "KPTF"
    ],
    "capture": [
        "['kap', 'cher']",
        "KPTR"
    ],
    "car": [
        "['kahr']",
        "KR"
    ],
    "car's": [
        "['kahr', \"'s\"]",
        "KRRS"
    ],
    "caramel": [
        "['kar', 'uh', 'muhl']",
        "KRML"
    ],
    "carat": [
        "['kar', 'uht']",
        "KRT"
    ],
    "carats": [
        "['kar', 'uht', 's']",
        "KRTS"
    ],
    "caravan": [
        "[kar,uh,van]",
        "KRFN"
    ],
    "carbon": [
        "['kahr', 'buhn']",
        "KRPN"
    ],
    "card": [
        "['kahrd']",
        "KRT"
    ],
    "cardiac": [
        "[kahr,dee,ak]",
        "KRTK"
    ],
    "cardigan": [
        "['kahr', 'di', 'guhn']",
        "KRTKN"
    ],
    "cards": [
        "['kahrd', 's']",
        "KRTS"
    ],
    "care": [
        "['kair']",
        "KR"
    ],
    "cared": [
        "['kair', 'd']",
        "KRT"
    ],
    "career": [
        "['kuh', 'reer']",
        "KRR"
    ],
    "careers": [
        "[kuh,reer,s]",
        "KRRS"
    ],
    "careful": [
        "['kair', 'fuhl']",
        "KRFL"
    ],
    "carefully": [
        "['kair', 'fuhl', 'ly']",
        "KRFL"
    ],
    "careless": [
        "['kair', 'lis']",
        "KRLS"
    ],
    "cares": [
        "['kair', 's']",
        "KRS"
    ],
    "caress": [
        "['kuh', 'res']",
        "KRS"
    ],
    "caressing": [
        "[kuh,res,ing]",
        "KRSNK"
    ],
    "carets": [
        "[kar,it,s]",
        "KRTS"
    ],
    "cargo's": [
        "[kahr,goh,'s]",
        "KRKS"
    ],
    "cargos": [
        "['kahr', 'goh', 's']",
        "KRKS"
    ],
    "caribbean": [
        "[kar,uh,bee,uhn]",
        "KRPN"
    ],
    "carlo": [
        [
            "kahr",
            "loh"
        ],
        "KRL"
    ],
    "carlos": [
        "[kahr,lohs]",
        "KRLS"
    ],
    "carnival": [
        "['kahr', 'nuh', 'vuhl']",
        "KRNFL"
    ],
    "carolinas": [
        "[kar,uh,lahy,nuh,s]",
        "KRLNS"
    ],
    "caroline": [
        "[kar,uh,lahyn]",
        "KRLN"
    ],
    "carpenter": [
        "[kahr,puhn,ter]",
        "KRPNTR"
    ],
    "carpet": [
        "['kahr', 'pit']",
        "KRPT"
    ],
    "carpets": [
        "['kahr', 'pit', 's']",
        "KRPTS"
    ],
    "carrera": [
        "['kuh', 'rair', 'uh']",
        "KRR"
    ],
    "carriage": [
        "['kar', 'ij']",
        "KRJ"
    ],
    "carrier": [
        "[kar,ee,er]",
        "KR"
    ],
    "carriers": [
        "[kar,ee,er,s]",
        "KRRS"
    ],
    "carrot": [
        "['kar', 'uht']",
        "KRT"
    ],
    "carrots": [
        "['kar', 'uht', 's']",
        "KRTS"
    ],
    "carry": [
        "['kar', 'ee']",
        "KR"
    ],
    "carrying": [
        "['kar', 'ee', 'ing']",
        "KRNK"
    ],
    "cars": [
        "['kahr', 's']",
        "KRS"
    ],
    "carson": [
        "[kahr,suhn]",
        "KRSN"
    ],
    "cart": [
        "['kahrt']",
        "KRT"
    ],
    "cartel": [
        "[kahr,tel]",
        "KRTL"
    ],
    "carter": [
        "['kahr', 'ter']",
        "KRTR"
    ],
    "carter's": [
        "[kahr,ter,'s]",
        "KRTRRS"
    ],
    "carters": [
        "['kahr', 'ter', 's']",
        "KRTRS"
    ],
    "cartier": [
        "['kahr', 'tee', 'ey']",
        "KRT"
    ],
    "carton": [
        "[kahr,tn]",
        "KRTN"
    ],
    "cartoon": [
        "['kahr', 'toon']",
        "KRTN"
    ],
    "cartoons": [
        "[kahr,toon,s]",
        "KRTNS"
    ],
    "cartridge": [
        "['kahr', 'trij']",
        "KRTRJ"
    ],
    "cartwheels": [
        "[kahrt,hweel,s]",
        "KRTLS"
    ],
    "carve": [
        "[kahrv]",
        "KRF"
    ],
    "carved": [
        "[kahrv,d]",
        "KRFT"
    ],
    "casa": [
        "['kah', 'suh']",
        "KS"
    ],
    "casanova": [
        "['kaz', 'uh', 'noh', 'vuh']",
        "KSNF"
    ],
    "cascade": [
        "[kas,keyd]",
        "KSKT"
    ],
    "case": [
        "['keys']",
        "KS"
    ],
    "cased": [
        "[keys,d]",
        "KST"
    ],
    "cases": [
        "['keys', 's']",
        "KSS"
    ],
    "cash": [
        "['kash']",
        "KX"
    ],
    "cashed": [
        "['kash', 'ed']",
        "KXT"
    ],
    "cashews": [
        "[kash,oo,s]",
        "KXS"
    ],
    "cashier": [
        "[ka,sheer]",
        "KX"
    ],
    "cashing": [
        "['kash', 'ing']",
        "KXNK"
    ],
    "cashmere": [
        "['kazh', 'meer']",
        "KXMR"
    ],
    "casino": [
        "['kuh', 'see', 'noh']",
        "KSN"
    ],
    "casinos": [
        "['kuh', 'see', 'noh', 's']",
        "KSNS"
    ],
    "cask": [
        "['kask']",
        "KSK"
    ],
    "casket": [
        "['kas', 'kit']",
        "KSKT"
    ],
    "caskets": [
        "[kas,kit,s]",
        "KSKTS"
    ],
    "casper": [
        "['kas', 'per']",
        "KSPR"
    ],
    "cassette": [
        "[kuh,set]",
        "KST"
    ],
    "cassidy": [
        [
            "kah",
            "si",
            "dee"
        ],
        "KST"
    ],
    "cassius": [
        "['kash', 'uhs']",
        "KSS"
    ],
    "cast": [
        "[kast]",
        "KST"
    ],
    "casting": [
        "['kas', 'ting']",
        "KSTNK"
    ],
    "castle": [
        "['kas', 'uhl']",
        "KSTL"
    ],
    "castor": [
        "[kas,ter]",
        "KSTR"
    ],
    "castro": [
        "[kas,troh]",
        "KSTR"
    ],
    "casually": [
        "[kazh,oo,uhl,ly]",
        "KSL"
    ],
    "casualty": [
        "[kazh,oo,uhl,tee]",
        "KSLT"
    ],
    "cat": [
        "['kat']",
        "KT"
    ],
    "catalog": [
        "['kat', 'l', 'awg']",
        "KTLK"
    ],
    "cataract": [
        "[kat,uh,rakt]",
        "KTRKT"
    ],
    "catch": [
        "['kach']",
        "KX"
    ],
    "catcher": [
        "[kach,er]",
        "KXR"
    ],
    "catches": [
        "[kach,es]",
        "KXS"
    ],
    "catching": [
        "['kach', 'ing']",
        "KXNK"
    ],
    "category": [
        "[kat,i,gawr,ee]",
        "KTKR"
    ],
    "cater": [
        "[key,ter]",
        "KTR"
    ],
    "caterpillar": [
        "['kat', 'uh', 'pil', 'er']",
        "KTRPLR"
    ],
    "catfish": [
        "[kat,fish]",
        "KTFX"
    ],
    "cathedral": [
        "['kuh', 'thee', 'druhl']",
        "K0TRL"
    ],
    "catholic": [
        "['kath', 'uh', 'lik']",
        "K0LK"
    ],
    "catholics": [
        "[kath,uh,lik,s]",
        "K0LKS"
    ],
    "cats": [
        "['kat', 's']",
        "KTS"
    ],
    "cattle": [
        "['kat', 'l']",
        "KTL"
    ],
    "caucasian": [
        "['kaw', 'key', 'zhuhn']",
        "KKSN"
    ],
    "caught": [
        "['kawt']",
        "KFT"
    ],
    "cause": [
        "['kawz']",
        "KS"
    ],
    "caused": [
        "['kawz', 'd']",
        "KST"
    ],
    "causing": [
        [
            "kawz",
            "ing"
        ],
        "KSNK"
    ],
    "caution": [
        "['kaw', 'shuhn']",
        "KXN"
    ],
    "cautious": [
        "['kaw', 'shuhs']",
        "KTS"
    ],
    "cavalier": [
        "['kav', 'uh', 'leer']",
        "KFL"
    ],
    "cave": [
        "[keyv]",
        "KF"
    ],
    "caviar": [
        "['kav', 'ee', 'ahr']",
        "KFR"
    ],
    "cavity": [
        "['kav', 'i', 'tee']",
        "KFT"
    ],
    "cayenne": [
        "['kahy', 'en']",
        "KN"
    ],
    "cc": [
        "[see,see]",
        "K"
    ],
    "cd": [
        "[kdm,m]",
        "KT"
    ],
    "ce": [
        "[sr,m]",
        "S"
    ],
    "cease": [
        "[sees]",
        "SS"
    ],
    "cedes": [
        "[seed,s]",
        "STS"
    ],
    "ceiling": [
        "['see', 'ling']",
        "SLNK"
    ],
    "ceilings": [
        "['see', 'ling', 's']",
        "SLNKS"
    ],
    "celebrate": [
        "['sel', 'uh', 'breyt']",
        "SLPRT"
    ],
    "celebrated": [
        "['sel', 'uh', 'brey', 'tid']",
        "SLPRTT"
    ],
    "celebration": [
        "['sel', 'uh', 'brey', 'shuhn']",
        "SLPRXN"
    ],
    "celebrity": [
        "[suh,leb,ri,tee]",
        "SLPRT"
    ],
    "celery": [
        "[sel,uh,ree]",
        "SLR"
    ],
    "celibate": [
        "['sel', 'uh', 'bit']",
        "SLPT"
    ],
    "cell": [
        "['sel']",
        "SL"
    ],
    "cellar": [
        "[sel,er]",
        "SLR"
    ],
    "cello": [
        "['chel', 'oh']",
        "SL"
    ],
    "cells": [
        "['sel', 's']",
        "SLS"
    ],
    "cellular": [
        "['sel', 'yuh', 'ler']",
        "SLLR"
    ],
    "celtics": [
        "['kel', 'tik', 's']",
        "SLTKS"
    ],
    "cement": [
        "['si', 'ment']",
        "SMNT"
    ],
    "cemetery": [
        "[sem,i,ter,ee]",
        "SMTR"
    ],
    "censorship": [
        "[sen,ser,ship]",
        "SNSRXP"
    ],
    "cent": [
        "['sent']",
        "SNT"
    ],
    "center": [
        "['sen', 'ter']",
        "SNTR"
    ],
    "centerfold": [
        "['sen', 'ter', 'fohld']",
        "SNTRFLT"
    ],
    "centipede": [
        "[sen,tuh,peed]",
        "SNTPT"
    ],
    "central": [
        "[sen,truhl]",
        "SNTRL"
    ],
    "centre": [
        "['sen', 'ter']",
        "SNTR"
    ],
    "cents": [
        "['sent', 's']",
        "SNTS"
    ],
    "century": [
        "['sen', 'chuh', 'ree']",
        "SNTR"
    ],
    "ceramic": [
        "[suh,ram,ik]",
        "SRMK"
    ],
    "cereal": [
        "['seer', 'ee', 'uhl']",
        "SRL"
    ],
    "cerebellum": [
        "['ser', 'uh', 'bel', 'uhm']",
        "SRPLM"
    ],
    "cerebral": [
        "['suh', 'ree', 'bruhl']",
        "SRPRL"
    ],
    "ceremony": [
        "[ser,uh,moh,nee]",
        "SRMN"
    ],
    "certain": [
        "['sur', 'tn']",
        "SRTN"
    ],
    "certainly": [
        "['sur', 'tn', 'lee']",
        "SRTNL"
    ],
    "certified": [
        "['sur', 'tuh', 'fahyd']",
        "SRTFT"
    ],
    "cha": [
        "['chah']",
        "X"
    ],
    "chad": [
        "[chad]",
        "XT"
    ],
    "chain": [
        "['cheyn']",
        "XN"
    ],
    "chain's": [
        "[cheyn,'s]",
        "XNNS"
    ],
    "chained": [
        "['cheyn', 'ed']",
        "XNT"
    ],
    "chains": [
        "['cheyn', 's']",
        "XNS"
    ],
    "chair": [
        "['chair']",
        "XR"
    ],
    "chairman": [
        "[chair,muhn]",
        "XRMN"
    ],
    "chairs": [
        "['chair', 's']",
        "XRS"
    ],
    "chalk": [
        "['chawk']",
        "XLK"
    ],
    "chalking": [
        "['chawk', 'ing']",
        "XLKNK"
    ],
    "challenge": [
        "['chal', 'inj']",
        "XLNJ"
    ],
    "challenged": [
        "[chal,injd]",
        "XLNJT"
    ],
    "challenger": [
        "[chal,in,jer]",
        "XLNKR"
    ],
    "chamber": [
        "['cheym', 'ber']",
        "XMPR"
    ],
    "chamberlain": [
        "['cheym', 'ber', 'lin']",
        "XMPRLN"
    ],
    "champ": [
        "['champ']",
        "XMP"
    ],
    "champagne": [
        "['sham', 'peyn']",
        "XMPN"
    ],
    "champagne's": [
        "[sham,peyn,'s]",
        "XMPNS"
    ],
    "champion": [
        "['cham', 'pee', 'uhn']",
        "XMPN"
    ],
    "champions": [
        "[cham,pee,uhn,s]",
        "XMPNS"
    ],
    "championship": [
        "['cham', 'pee', 'uhn', 'ship']",
        "XMPNXP"
    ],
    "chance": [
        "['chans']",
        "XNS"
    ],
    "chances": [
        "['chans', 's']",
        "XNSS"
    ],
    "chandelier": [
        "['shan', 'dl', 'eer']",
        "XNTL"
    ],
    "chandeliers": [
        "['shan', 'dl', 'eer', 's']",
        "XNTLRS"
    ],
    "chanel": [
        "['shuh', 'nel']",
        "XNL"
    ],
    "change": [
        "['cheynj']",
        "XNJ"
    ],
    "changed": [
        "['cheynj', 'd']",
        "XNJT"
    ],
    "changer": [
        "[cheyn,jer]",
        "XNKR"
    ],
    "changes": [
        "['cheynj', 's']",
        "XNJS"
    ],
    "channel": [
        "['chan', 'l']",
        "XNL"
    ],
    "channels": [
        "['chan', 'l', 's']",
        "XNLS"
    ],
    "chant": [
        "[chant]",
        "XNT"
    ],
    "chaos": [
        "[key,os]",
        "XS"
    ],
    "chapter": [
        "['chap', 'ter']",
        "XPTR"
    ],
    "chapters": [
        "[chap,ter,s]",
        "XPTRS"
    ],
    "character": [
        "[kar,ik,ter]",
        "KRKTR"
    ],
    "characters": [
        "[kar,ik,ter,s]",
        "KRKTRS"
    ],
    "charcoal": [
        "['chahr', 'kohl']",
        "XRKL"
    ],
    "charge": [
        "['chahrj']",
        "XRJ"
    ],
    "charged": [
        "['chahrjd']",
        "XRJT"
    ],
    "charger": [
        "['chahr', 'jer']",
        "XRKR"
    ],
    "charges": [
        "['chahrj', 's']",
        "XRJS"
    ],
    "chariot": [
        "['char', 'ee', 'uht']",
        "XRT"
    ],
    "charisma": [
        "['kuh', 'riz', 'muh']",
        "KRSM"
    ],
    "charity": [
        "['char', 'i', 'tee']",
        "XRT"
    ],
    "charles": [
        "['chahrlz']",
        "XRLS"
    ],
    "charlie": [
        "['chahr', 'lee']",
        "XRL"
    ],
    "charm": [
        "['chahrm']",
        "XRM"
    ],
    "charming": [
        "['chahr', 'ming']",
        "XRMNK"
    ],
    "charms": [
        "['chahrm', 's']",
        "XRMS"
    ],
    "chart": [
        "['chahrt']",
        "XRT"
    ],
    "charter": [
        "['chahr', 'ter']",
        "XRTR"
    ],
    "chartered": [
        "['chahr', 'ter', 'ed']",
        "XRTRT"
    ],
    "charts": [
        "['chahrt', 's']",
        "XRTS"
    ],
    "chase": [
        "['cheys']",
        "XS"
    ],
    "chased": [
        "['cheys', 'd']",
        "XST"
    ],
    "chaser": [
        "['chey', 'ser']",
        "XSR"
    ],
    "chasers": [
        "['chey', 'ser', 's']",
        "XSRS"
    ],
    "chasing": [
        "['chey', 'sing']",
        "XSNK"
    ],
    "chat": [
        "['chat']",
        "XT"
    ],
    "chatter": [
        "['chat', 'er']",
        "XTR"
    ],
    "chatting": [
        "[chat,ting]",
        "XTNK"
    ],
    "chatty": [
        "[chat,ee]",
        "XT"
    ],
    "chauffeur": [
        "['shoh', 'fer']",
        "XFR"
    ],
    "chauffeured": [
        "[shoh,fer,ed]",
        "XFRT"
    ],
    "cheap": [
        "['cheep']",
        "XP"
    ],
    "cheaper": [
        "['cheep', 'er']",
        "XPR"
    ],
    "cheat": [
        "['cheet']",
        "XT"
    ],
    "cheated": [
        "['cheet', 'ed']",
        "XTT"
    ],
    "cheater": [
        "['chee', 'ter']",
        "XTR"
    ],
    "cheating": [
        "['cheet', 'ing']",
        "XTNK"
    ],
    "check": [
        "['chek']",
        "XK"
    ],
    "check's": [
        "['chek', \"'s\"]",
        "XKK"
    ],
    "checked": [
        "['chekt']",
        "XKT"
    ],
    "checkers": [
        "['chek', 'er', 's']",
        "XKRS"
    ],
    "checking": [
        "['chek', 'ing']",
        "XKNK"
    ],
    "checklist": [
        "['chek', 'list']",
        "XKLST"
    ],
    "checks": [
        "['chek', 's']",
        "XKS"
    ],
    "cheddar": [
        "['ched', 'er']",
        "XTR"
    ],
    "cheek": [
        "[cheek]",
        "XK"
    ],
    "cheeks": [
        "['cheek', 's']",
        "XKS"
    ],
    "cheer": [
        "[cheer]",
        "XR"
    ],
    "cheerios": [
        "[cheer,ee,oh,s]",
        "XRS"
    ],
    "cheerleader": [
        "['cheer', 'lee', 'der']",
        "XRLTR"
    ],
    "cheerleaders": [
        "[cheer,lee,der,s]",
        "XRLTRS"
    ],
    "cheers": [
        "['cheer', 's']",
        "XRS"
    ],
    "cheese": [
        "['cheez']",
        "XS"
    ],
    "cheesecake": [
        "['cheez', 'keyk']",
        "XSKK"
    ],
    "cheesy": [
        "[chee,zee]",
        "XS"
    ],
    "cheetah": [
        "['chee', 'tuh']",
        "XT"
    ],
    "chef": [
        "['shef']",
        "XF"
    ],
    "chemical": [
        "[kem,i,kuhl]",
        "KMKL"
    ],
    "chemicals": [
        "['kem', 'i', 'kuhl', 's']",
        "KMKLS"
    ],
    "chemist": [
        "['kem', 'ist']",
        "KMST"
    ],
    "chemistry": [
        "['kem', 'uh', 'stree']",
        "KMSTR"
    ],
    "cheque": [
        "['chek']",
        "XK"
    ],
    "cheques": [
        "[chek,s]",
        "XKS"
    ],
    "cherish": [
        "['cher', 'ish']",
        "XRX"
    ],
    "cherry": [
        "['cher', 'ee']",
        "XR"
    ],
    "chess": [
        "['ches']",
        "XS"
    ],
    "chest": [
        "['chest']",
        "XST"
    ],
    "chests": [
        "[chest,s]",
        "XSTS"
    ],
    "chevron": [
        "[shev,ruhn]",
        "XFRN"
    ],
    "chevy": [
        "['chev', 'ee']",
        "XF"
    ],
    "chevy's": [
        "[chev,ee,'s]",
        "XFS"
    ],
    "chew": [
        "['choo']",
        "X"
    ],
    "chewed": [
        "['choo', 'ed']",
        "XT"
    ],
    "chewing": [
        "['choo', 'ing']",
        "XNK"
    ],
    "chi": [
        "['kahy']",
        "X"
    ],
    "chia": [
        "['chee', 'uh']",
        "K"
    ],
    "chic": [
        "[sheek]",
        "XK"
    ],
    "chicago": [
        "['shi', 'kah', 'goh']",
        "XKK"
    ],
    "chick": [
        "['chik']",
        "XK"
    ],
    "chicken": [
        "['chik', 'uhn']",
        "XKN"
    ],
    "chickens": [
        "['chik', 'uhn', 's']",
        "XKNS"
    ],
    "chicks": [
        "['chik', 's']",
        "XKS"
    ],
    "chico": [
        "['chee', 'koh']",
        "XK"
    ],
    "chief": [
        "[cheef]",
        "XF"
    ],
    "child": [
        "['chahyld']",
        "XLT"
    ],
    "childhood": [
        "[chahyld,hood]",
        "XLTT"
    ],
    "childish": [
        "['chahyl', 'dish']",
        "XLTX"
    ],
    "children": [
        "['chil', 'druhn']",
        "XLTRN"
    ],
    "chill": [
        "['chil']",
        "XL"
    ],
    "chilled": [
        "[chil,ed]",
        "XLT"
    ],
    "chiller": [
        "[chil,er]",
        "XLR"
    ],
    "chilling": [
        "['chil', 'ing']",
        "XLNK"
    ],
    "chills": [
        "['chil', 's']",
        "XLS"
    ],
    "chilly": [
        "['chil', 'ee']",
        "XL"
    ],
    "chimney": [
        "['chim', 'nee']",
        "XMN"
    ],
    "chimp": [
        "['chimp']",
        "XMP"
    ],
    "china": [
        "['chahy', 'nuh']",
        "XN"
    ],
    "chinchilla": [
        "['chin', 'chil', 'uh']",
        "XNXL"
    ],
    "chinchillas": [
        "[chin,chil,uh,s]",
        "XNXLS"
    ],
    "chinese": [
        "['chahy', 'neez']",
        "XNS"
    ],
    "chink": [
        "[chingk]",
        "XNK"
    ],
    "chino": [
        "['chee', 'noh']",
        "XN"
    ],
    "chip": [
        "['chip']",
        "XP"
    ],
    "chipped": [
        "[chip,ped]",
        "XPT"
    ],
    "chips": [
        "['chip', 's']",
        "XPS"
    ],
    "chiquita": [
        "['chi', 'kee', 'tuh']",
        "XKT"
    ],
    "chirp": [
        "['churp']",
        "XRP"
    ],
    "chirping": [
        "[churp,ing]",
        "XRPNK"
    ],
    "chit": [
        "['chit']",
        "XT"
    ],
    "chlorine": [
        "['klawr', 'een']",
        "KLRN"
    ],
    "chock": [
        "['chok']",
        "XK"
    ],
    "chocolate": [
        "['chaw', 'kuh', 'lit']",
        "XKLT"
    ],
    "choice": [
        "['chois']",
        "XS"
    ],
    "choices": [
        "['chois', 's']",
        "XSS"
    ],
    "choir": [
        "['kwahyuhr']",
        "XR"
    ],
    "choke": [
        "['chohk']",
        "XK"
    ],
    "choked": [
        "['chohk', 'd']",
        "XKT"
    ],
    "chokehold": [
        "['chohk', 'hohld']",
        "XKHLT"
    ],
    "choker": [
        "['choh', 'ker']",
        "XKR"
    ],
    "chokers": [
        "['choh', 'ker', 's']",
        "XKRS"
    ],
    "choking": [
        "['choh', 'king']",
        "XKNK"
    ],
    "choose": [
        "['chooz']",
        "XS"
    ],
    "choosey": [
        [
            "chooz",
            "ey"
        ],
        "XS"
    ],
    "choosing": [
        [
            "chooz",
            "ing"
        ],
        "XSNK"
    ],
    "choosy": [
        "['choo', 'zee']",
        "XS"
    ],
    "chop": [
        "['chop']",
        "XP"
    ],
    "choppa": [
        [
            "chop",
            "pah"
        ],
        "XP"
    ],
    "chopped": [
        "['chopt']",
        "XPT"
    ],
    "chopper": [
        "['chop', 'er']",
        "XPR"
    ],
    "choppers": [
        "['chop', 'er', 's']",
        "XPRS"
    ],
    "chopping": [
        "['chop', 'ping']",
        "XPNK"
    ],
    "chops": [
        "[chop,s]",
        "XPS"
    ],
    "chopsticks": [
        "['chop', 'stiks']",
        "XPSTKS"
    ],
    "chords": [
        "[kawrd,s]",
        "KRTS"
    ],
    "chores": [
        "[chawr,s]",
        "XRS"
    ],
    "chorus": [
        "['kawr', 'uhs']",
        "KRS"
    ],
    "chose": [
        "['chohz']",
        "XS"
    ],
    "chosen": [
        "['choh', 'zuhn']",
        "XSN"
    ],
    "chow": [
        "[chou]",
        "X"
    ],
    "chows": [
        "[chou,s]",
        "XS"
    ],
    "chris": [
        "['kris']",
        "KRS"
    ],
    "christ": [
        "['krahyst']",
        "KRST"
    ],
    "christian": [
        "['kris', 'chuhn']",
        "KRSXN"
    ],
    "christians": [
        "['kris', 'chuhn', 's']",
        "KRSXNS"
    ],
    "christmas": [
        "['kris', 'muhs']",
        "KRSTMS"
    ],
    "christopher": [
        "['kris', 'tuh', 'fer']",
        "KRSTFR"
    ],
    "chrome": [
        "['krohm']",
        "KRM"
    ],
    "chromed": [
        "[krohm,d]",
        "KRMT"
    ],
    "chronic": [
        "['kron', 'ik']",
        "KRNK"
    ],
    "chubby": [
        "[chuhb,ee]",
        "XP"
    ],
    "chuck": [
        "['chuhk']",
        "XK"
    ],
    "chucking": [
        "[chuhk,ing]",
        "XKNK"
    ],
    "chucks": [
        "[chuhk,s]",
        "XKS"
    ],
    "chug": [
        "['chuhg']",
        "XK"
    ],
    "chugging": [
        "[chuhg,ging]",
        "XKNK"
    ],
    "chump": [
        "[chuhmp]",
        "XMP"
    ],
    "chumps": [
        "[chuhmp,s]",
        "XMPS"
    ],
    "chunk": [
        "['chuhngk']",
        "XNK"
    ],
    "chunky": [
        "[chuhng,kee]",
        "XNK"
    ],
    "church": [
        "['church']",
        "XRX"
    ],
    "churches": [
        "[church,es]",
        "XRXS"
    ],
    "churn": [
        "[churn]",
        "XRN"
    ],
    "cider": [
        "[sahy,der]",
        "STR"
    ],
    "cig": [
        "['sig']",
        "SK"
    ],
    "cigar": [
        "['si', 'gahr']",
        "SKR"
    ],
    "cigarette": [
        "['sig', 'uh', 'ret']",
        "SKRT"
    ],
    "cigarettes": [
        "['sig', 'uh', 'ret', 's']",
        "SKRTS"
    ],
    "cigarillo": [
        "[sig,uh,ril,oh]",
        "SKRL"
    ],
    "cigarillos": [
        "[sig,uh,ril,oh,s]",
        "SKRLS"
    ],
    "cigars": [
        "[si,gahr,s]",
        "SKRS"
    ],
    "cincinnati": [
        "[sin,suh,nat,ee]",
        "SNSNT"
    ],
    "cinco": [
        [
            "sin",
            "koh"
        ],
        "SNK"
    ],
    "cinderella": [
        "['sin', 'duh', 'rel', 'uh']",
        "SNTRL"
    ],
    "cinema": [
        "[sin,uh,muh]",
        "SNM"
    ],
    "cinematic": [
        "[sin,uh,muh,tic]",
        "SNMTK"
    ],
    "cinnamon": [
        "['sin', 'uh', 'muhn']",
        "SNMN"
    ],
    "cipher": [
        "[sahy,fer]",
        "SFR"
    ],
    "circle": [
        "['sur', 'kuhl']",
        "SRKL"
    ],
    "circles": [
        "['sur', 'kuhl', 's']",
        "SRKLS"
    ],
    "circular": [
        "[sur,kyuh,ler]",
        "SRKLR"
    ],
    "circumstances": [
        "[sur,kuhm,stansor,s]",
        "SRKMSTNSS"
    ],
    "circus": [
        "['sur', 'kuhs']",
        "SRKS"
    ],
    "cirque": [
        "['surk']",
        "SRK"
    ],
    "citizens": [
        "['sit', 'uh', 'zuhn', 's']",
        "STSNS"
    ],
    "city": [
        "['sit', 'ee']",
        "ST"
    ],
    "city's": [
        "[sit,ee,'s]",
        "STS"
    ],
    "citywide": [
        "[sit,ee,wahyd]",
        "STT"
    ],
    "civic": [
        "['siv', 'ik']",
        "SFK"
    ],
    "civil": [
        "['siv', 'uhl']",
        "SFL"
    ],
    "civilian": [
        "['si', 'vil', 'yuhn']",
        "SFLN"
    ],
    "civilians": [
        "['si', 'vil', 'yuhn', 's']",
        "SFLNS"
    ],
    "civilized": [
        "[siv,uh,lahyzd]",
        "SFLST"
    ],
    "cl": [
        "[(s,l)]",
        "KL"
    ],
    "clack": [
        "['klak']",
        "KLK"
    ],
    "claim": [
        "['kleym']",
        "KLM"
    ],
    "claimed": [
        "[kleym,ed]",
        "KLMT"
    ],
    "claiming": [
        "['kleym', 'ing']",
        "KLMNK"
    ],
    "claims": [
        "['kleym', 's']",
        "KLMS"
    ],
    "clams": [
        "['klam', 's']",
        "KLMS"
    ],
    "clan": [
        "['klan']",
        "KLN"
    ],
    "clank": [
        "[klangk]",
        "KLNK"
    ],
    "clap": [
        "['klap']",
        "KLP"
    ],
    "clapped": [
        "['klap', 'ped']",
        "KLPT"
    ],
    "clapping": [
        "['klap', 'ping']",
        "KLPNK"
    ],
    "claps": [
        "[klap,s]",
        "KLPS"
    ],
    "clarity": [
        "['klar', 'i', 'tee']",
        "KLRT"
    ],
    "clark": [
        "['klahrk']",
        "KLRK"
    ],
    "clash": [
        "[klash]",
        "KLX"
    ],
    "clashing": [
        "['klash', 'ing']",
        "KLXNK"
    ],
    "class": [
        "['klas']",
        "KLS"
    ],
    "classes": [
        "[klas,es]",
        "KLSS"
    ],
    "classic": [
        "['klas', 'ik']",
        "KLSK"
    ],
    "classical": [
        "['klas', 'i', 'kuhl']",
        "KLSKL"
    ],
    "classics": [
        "[klas,ik,s]",
        "KLSKS"
    ],
    "classmates": [
        "['klas', 'meyt', 's']",
        "KLSMTS"
    ],
    "classroom": [
        "['klas', 'room']",
        "KLSRM"
    ],
    "classy": [
        "['klas', 'ee']",
        "KLS"
    ],
    "clause": [
        "[klawz]",
        "KLS"
    ],
    "clay": [
        "['kley']",
        "KL"
    ],
    "clean": [
        "['kleen']",
        "KLN"
    ],
    "cleaned": [
        "['kleen', 'ed']",
        "KLNT"
    ],
    "cleaner": [
        "['klee', 'ner']",
        "KLNR"
    ],
    "cleaners": [
        "[klee,ner,s]",
        "KLNRS"
    ],
    "cleanest": [
        "['kleen', 'est']",
        "KLNST"
    ],
    "cleaning": [
        "['klee', 'ning']",
        "KLNNK"
    ],
    "clear": [
        "['kleer']",
        "KLR"
    ],
    "clearance": [
        "[kleer,uhns]",
        "KLRNS"
    ],
    "cleared": [
        "['kleer', 'ed']",
        "KLRT"
    ],
    "clearer": [
        "['kleer', 'er']",
        "KLRR"
    ],
    "clearing": [
        "['kleer', 'ing']",
        "KLRNK"
    ],
    "clearly": [
        "['kleer', 'lee']",
        "KLRL"
    ],
    "cleat": [
        "[kleet]",
        "KLT"
    ],
    "cleats": [
        "['kleet', 's']",
        "KLTS"
    ],
    "cleavage": [
        "['klee', 'vij']",
        "KLFJ"
    ],
    "cleaver": [
        "['klee', 'ver']",
        "KLFR"
    ],
    "cleo": [
        "['klee', 'oh']",
        "KL"
    ],
    "cleveland": [
        "['kleev', 'luhnd']",
        "KLFLNT"
    ],
    "clever": [
        "['klev', 'er']",
        "KLFR"
    ],
    "click": [
        "['klik']",
        "KLK"
    ],
    "clicking": [
        "[klik,ing]",
        "KLKNK"
    ],
    "clientele": [
        "[klahy,uhn,tel]",
        "KLNTL"
    ],
    "cliff": [
        "[klif]",
        "KLF"
    ],
    "climate": [
        "['klahy', 'mit']",
        "KLMT"
    ],
    "climax": [
        "['klahy', 'maks']",
        "KLMKS"
    ],
    "climb": [
        "['klahym']",
        "KLMP"
    ],
    "climbed": [
        "[klahym,ed]",
        "KLMPT"
    ],
    "climbing": [
        "['klahym', 'ing']",
        "KLMPNK"
    ],
    "cling": [
        "[kling]",
        "KLNK"
    ],
    "clinic": [
        "['klin', 'ik']",
        "KLNK"
    ],
    "clink": [
        "[klingk]",
        "KLNK"
    ],
    "clinking": [
        "['klingk', 'ing']",
        "KLNKNK"
    ],
    "clinton": [
        "['klin', 'tn']",
        "KLNTN"
    ],
    "clip": [
        "['klip']",
        "KLP"
    ],
    "clippers": [
        "['klip', 'er', 's']",
        "KLPRS"
    ],
    "clips": [
        "['klip', 's']",
        "KLPS"
    ],
    "clique": [
        "['kleek']",
        "KLK"
    ],
    "clique's": [
        "['kleek', \"'s\"]",
        "KLKS"
    ],
    "clit": [
        "[klit]",
        "KLT"
    ],
    "clitoris": [
        "['klit', 'er', 'is']",
        "KLTRS"
    ],
    "clock": [
        "['klok']",
        "KLK"
    ],
    "clocking": [
        "['klok', 'ing']",
        "KLKNK"
    ],
    "clocks": [
        "['klok', 's']",
        "KLKS"
    ],
    "clockwork": [
        "['klok', 'wurk']",
        "KLKRK"
    ],
    "clone": [
        "['klohn']",
        "KLN"
    ],
    "cloned": [
        "[klohn,d]",
        "KLNT"
    ],
    "clones": [
        "['klohn', 's']",
        "KLNS"
    ],
    "cloning": [
        "['kloh', 'ning']",
        "KLNNK"
    ],
    "close": [
        "['verbklohz']",
        "KLS"
    ],
    "closed": [
        "['klohzd']",
        "KLST"
    ],
    "closely": [
        "[verbklohz,ly]",
        "KLSL"
    ],
    "closer": [
        "['kloh', 'zer']",
        "KLSR"
    ],
    "closes": [
        "['verbklohz', 's']",
        "KLSS"
    ],
    "closest": [
        "[verbklohz,st]",
        "KLSST"
    ],
    "closet": [
        "['kloz', 'it']",
        "KLST"
    ],
    "closets": [
        "[kloz,it,s]",
        "KLSTS"
    ],
    "closing": [
        "['kloh', 'zing']",
        "KLSNK"
    ],
    "closure": [
        "['kloh', 'zher']",
        "KLSR"
    ],
    "clot": [
        "['klot']",
        "KLT"
    ],
    "cloth": [
        "['klawth']",
        "KL0"
    ],
    "clothes": [
        "['klohz']",
        "KL0S"
    ],
    "clothing": [
        "['kloh', 'thing']",
        "KL0NK"
    ],
    "cloud": [
        "['kloud']",
        "KLT"
    ],
    "clouded": [
        "[klou,did]",
        "KLTT"
    ],
    "clouds": [
        "['kloud', 's']",
        "KLTS"
    ],
    "cloudy": [
        "['klou', 'dee']",
        "KLT"
    ],
    "clout": [
        "['klout']",
        "KLT"
    ],
    "clover": [
        "[kloh,ver]",
        "KLFR"
    ],
    "clown": [
        "['kloun']",
        "KLN"
    ],
    "clowning": [
        "[kloun,ing]",
        "KLNNK"
    ],
    "clowns": [
        "['kloun', 's']",
        "KLNS"
    ],
    "club": [
        "['kluhb']",
        "KLP"
    ],
    "clubbing": [
        "['kluhb', 'ing']",
        "KLPNK"
    ],
    "clubs": [
        "['kluhb', 's']",
        "KLPS"
    ],
    "clucking": [
        "[kluhk,ing]",
        "KLKNK"
    ],
    "clue": [
        "['kloo']",
        "KL"
    ],
    "clueless": [
        "['kloo', 'lis']",
        "KLLS"
    ],
    "clues": [
        "['kloo', 's']",
        "KLS"
    ],
    "clutch": [
        "[kluhch]",
        "KLX"
    ],
    "clutching": [
        "['kluhch', 'ing']",
        "KLXNK"
    ],
    "cluttered": [
        "[kluht,er,ed]",
        "KLTRT"
    ],
    "clyde": [
        "['klahyd']",
        "KLT"
    ],
    "co": [
        "['kblt']",
        "K"
    ],
    "coach": [
        "['kohch']",
        "KX"
    ],
    "coaches": [
        "['kohch', 'es']",
        "KXS"
    ],
    "coaching": [
        "[kohch,ing]",
        "KXNK"
    ],
    "coals": [
        "[kohl,s]",
        "KLS"
    ],
    "coast": [
        "['kohst']",
        "KST"
    ],
    "coaster": [
        "['koh', 'ster']",
        "KSTR"
    ],
    "coasting": [
        "['kohst', 'ing']",
        "KSTNK"
    ],
    "coat": [
        "['koht']",
        "KT"
    ],
    "coated": [
        "['koh', 'tid']",
        "KTT"
    ],
    "coats": [
        "['koht', 's']",
        "KTS"
    ],
    "cob": [
        "[kob]",
        "KP"
    ],
    "cobra": [
        "['koh', 'bruh']",
        "KPR"
    ],
    "coca": [
        "['koh', 'kuh']",
        "KK"
    ],
    "cocaine": [
        "['koh', 'keyn']",
        "KKN"
    ],
    "cochran": [
        "['kok', 'ruhn']",
        "KKRN"
    ],
    "cock": [
        "['kok']",
        "KK"
    ],
    "cocked": [
        "['kok', 'ed']",
        "KKT"
    ],
    "cocking": [
        "['kok', 'ing']",
        "KKNK"
    ],
    "cockpit": [
        "[kok,pit]",
        "KKPT"
    ],
    "cockroaches": [
        "['kok', 'rohch', 'es']",
        "KKRXS"
    ],
    "cocksucker": [
        "[kok,suhk,er]",
        "KKSKR"
    ],
    "cocksuckers": [
        "['kok', 'suhk', 'er', 's']",
        "KKSKRS"
    ],
    "cocktail": [
        "['kok', 'teyl']",
        "KKTL"
    ],
    "cocktails": [
        "['kok', 'teyl', 's']",
        "KKTLS"
    ],
    "cocky": [
        "['kok', 'ee']",
        "KK"
    ],
    "coco": [
        "['koh', 'koh']",
        "KK"
    ],
    "cocoa": [
        "['koh', 'koh']",
        "KK"
    ],
    "coconut": [
        "['koh', 'kuh', 'nuht']",
        "KKNT"
    ],
    "cocoon": [
        "['kuh', 'koon']",
        "KKN"
    ],
    "code": [
        "['kohd']",
        "KT"
    ],
    "codeine": [
        "['koh', 'deen']",
        "KTN"
    ],
    "codes": [
        "['kohd', 's']",
        "KTS"
    ],
    "cody": [
        "['koh', 'dee']",
        "KT"
    ],
    "coffee": [
        "['kaw', 'fee']",
        "KF"
    ],
    "coffin": [
        "['kaw', 'fin']",
        "KFN"
    ],
    "coffins": [
        "[kaw,fin,s]",
        "KFNS"
    ],
    "cognac": [
        "[kohn,yak]",
        "KNK"
    ],
    "coin": [
        "[koin]",
        "KN"
    ],
    "coincidental": [
        "[koh,in,si,den,tl]",
        "KNSTNTL"
    ],
    "coins": [
        "['koin', 's']",
        "KNS"
    ],
    "coke": [
        "['kohk']",
        "KK"
    ],
    "cola": [
        "['koh', 'luh']",
        "KL"
    ],
    "colada": [
        "['koh', 'lah', 'duh']",
        "KLT"
    ],
    "cold": [
        "['kohld']",
        "KLT"
    ],
    "colder": [
        "['kohld', 'er']",
        "KLTR"
    ],
    "coldest": [
        "['kohld', 'est']",
        "KLTST"
    ],
    "cole": [
        "['kohl']",
        "KL"
    ],
    "colgate": [
        [
            "kol",
            "geyt"
        ],
        "KLKT"
    ],
    "collab": [
        [
            "kol",
            "lab"
        ],
        "KLP"
    ],
    "collage": [
        "['kuh', 'lahzh']",
        "KLJ"
    ],
    "collagen": [
        "[kol,uh,juhn]",
        "KLJN"
    ],
    "collapse": [
        "[kuh,laps]",
        "KLPS"
    ],
    "collar": [
        "['kol', 'er']",
        "KLR"
    ],
    "collard": [
        "['kol', 'erd']",
        "KLRT"
    ],
    "collared": [
        "['kol', 'er', 'ed']",
        "KLRT"
    ],
    "collars": [
        "['kol', 'er', 's']",
        "KLRS"
    ],
    "collect": [
        "['kuh', 'lekt']",
        "KLKT"
    ],
    "collecting": [
        "['kuh', 'lekt', 'ing']",
        "KLKTNK"
    ],
    "collection": [
        "['kuh', 'lek', 'shuhn']",
        "KLKXN"
    ],
    "college": [
        "['kol', 'ij']",
        "KLJ"
    ],
    "collide": [
        "['kuh', 'lahyd']",
        "KLT"
    ],
    "collins": [
        "[kol,inz]",
        "KLNS"
    ],
    "collision": [
        "['kuh', 'lizh', 'uhn']",
        "KLSN"
    ],
    "cologne": [
        "['kuh', 'lohn']",
        "KLN"
    ],
    "colombia": [
        "[kuh,luhm,bee,uh]",
        "KLMP"
    ],
    "colombian": [
        "[kuh,luhm,bee,uh,n]",
        "KLMPN"
    ],
    "colon": [
        "['koh', 'luhn']",
        "KLN"
    ],
    "color": [
        "['kuhl', 'er']",
        "KLR"
    ],
    "colorado": [
        "['kol', 'uh', 'rad', 'oh']",
        "KLRT"
    ],
    "colored": [
        "['kuhl', 'erd']",
        "KLRT"
    ],
    "colorful": [
        "['kuhl', 'er', 'fuhl']",
        "KLRFL"
    ],
    "colors": [
        "['kuhl', 'er', 's']",
        "KLRS"
    ],
    "colossal": [
        "['kuh', 'los', 'uhl']",
        "KLSL"
    ],
    "colour": [
        "['kuhl', 'er']",
        "KLR"
    ],
    "colours": [
        "[kuhl,er,s]",
        "KLRS"
    ],
    "columbine": [
        "['kol', 'uhm', 'bahyn']",
        "KLMPN"
    ],
    "columbus": [
        "['kuh', 'luhm', 'buhs']",
        "KLMPS"
    ],
    "column": [
        "[kol,uhm]",
        "KLMN"
    ],
    "coma": [
        "['koh', 'muh']",
        "KM"
    ],
    "comatose": [
        "['kom', 'uh', 'tohs']",
        "KMTS"
    ],
    "comb": [
        "['kohm']",
        "KMP"
    ],
    "combat": [
        "['verbkuhm', 'bat']",
        "KMPT"
    ],
    "combination": [
        "['kom', 'buh', 'ney', 'shuhn']",
        "KMPNXN"
    ],
    "combine": [
        "['verbkuhm', 'bahynfor1']",
        "KMPN"
    ],
    "combined": [
        "[kuhm,bahynd]",
        "KMPNT"
    ],
    "combo": [
        "['kom', 'boh']",
        "KMP"
    ],
    "combs": [
        "['kohm', 's']",
        "KMPS"
    ],
    "come": [
        "['kuhm']",
        "KM"
    ],
    "comeback": [
        "['kuhm', 'bak']",
        "KMPK"
    ],
    "comedy": [
        "[kom,i,dee]",
        "KMT"
    ],
    "comes": [
        "['koh', 'meez']",
        "KMS"
    ],
    "comet": [
        "[kom,it]",
        "KMT"
    ],
    "comfort": [
        "[kuhm,fert]",
        "KMFRT"
    ],
    "comfortable": [
        "['kuhmf', 'tuh', 'buhl']",
        "KMFRTPL"
    ],
    "comfy": [
        "[kuhm,fee]",
        "KMF"
    ],
    "comic": [
        "[kom,ik]",
        "KMK"
    ],
    "comics": [
        "[kom,ik,s]",
        "KMKS"
    ],
    "coming": [
        "['kuhm', 'ing']",
        "KMNK"
    ],
    "comma": [
        "['kom', 'uh']",
        "KM"
    ],
    "command": [
        "[kuh,mand]",
        "KMNT"
    ],
    "commander": [
        "[kuh,man,der]",
        "KMNTR"
    ],
    "commanding": [
        "[kuh,man,ding]",
        "KMNTNK"
    ],
    "commandments": [
        "[kuh,mand,muhnt,s]",
        "KMNTMNTS"
    ],
    "commando": [
        "['kuh', 'man', 'doh']",
        "KMNT"
    ],
    "commands": [
        "['kuh', 'mand', 's']",
        "KMNTS"
    ],
    "commas": [
        "['kom', 'uh', 's']",
        "KMS"
    ],
    "commence": [
        "[kuh,mens]",
        "KMNS"
    ],
    "comment": [
        "[kom,ent]",
        "KMNT"
    ],
    "comments": [
        "['kom', 'ent', 's']",
        "KMNTS"
    ],
    "commercial": [
        "['kuh', 'mur', 'shuhl']",
        "KMRSL"
    ],
    "commissary": [
        "['kom', 'uh', 'ser', 'ee']",
        "KMSR"
    ],
    "commission": [
        "[kuh,mish,uhn]",
        "KMSN"
    ],
    "commit": [
        "['kuh', 'mit']",
        "KMT"
    ],
    "commitment": [
        "['kuh', 'mit', 'muhnt']",
        "KMTMNT"
    ],
    "committed": [
        "['kuh', 'mit', 'id']",
        "KMTT"
    ],
    "committee": [
        "['kuh', 'mit', 'ee']",
        "KMT"
    ],
    "committing": [
        "['kuh', 'mit', 'ting']",
        "KMTNK"
    ],
    "common": [
        "['kom', 'uhn']",
        "KMN"
    ],
    "commotion": [
        "['kuh', 'moh', 'shuhn']",
        "KMXN"
    ],
    "communicate": [
        "[kuh,myoo,ni,keyt]",
        "KMNKT"
    ],
    "communication": [
        "[kuh,myoo,ni,key,shuhn]",
        "KMNKXN"
    ],
    "community": [
        "['kuh', 'myoo', 'ni', 'tee']",
        "KMNT"
    ],
    "companies": [
        [
            "kuhnm",
            "puh",
            "nees"
        ],
        "KMPNS"
    ],
    "company": [
        "['kuhm', 'puh', 'nee']",
        "KMPN"
    ],
    "compare": [
        "['kuhm', 'pair']",
        "KMPR"
    ],
    "compared": [
        "['kuhm', 'pair', 'd']",
        "KMPRT"
    ],
    "compares": [
        "[kuhm,pair,s]",
        "KMPRS"
    ],
    "comparison": [
        "['kuhm', 'par', 'uh', 'suhn']",
        "KMPRSN"
    ],
    "compartment": [
        "[kuhm,pahrt,muhnt]",
        "KMPRTMNT"
    ],
    "compass": [
        "[kuhm,puhs]",
        "KMPS"
    ],
    "compete": [
        "['kuhm', 'peet']",
        "KMPT"
    ],
    "competition": [
        "['kom', 'pi', 'tish', 'uhn']",
        "KMPTXN"
    ],
    "competitors": [
        "[kuhm,pet,i,ter,s]",
        "KMPTTRS"
    ],
    "complacent": [
        "[kuhm,pley,suhnt]",
        "KMPLSNT"
    ],
    "complain": [
        "['kuhm', 'pleyn']",
        "KMPLN"
    ],
    "complaining": [
        "['kuhm', 'pleyn', 'ing']",
        "KMPLNNK"
    ],
    "complains": [
        "[kuhm,pleyn,s]",
        "KMPLNS"
    ],
    "complaints": [
        "[kuhm,pleynt,s]",
        "KMPLNTS"
    ],
    "complete": [
        "['kuhm', 'pleet']",
        "KMPLT"
    ],
    "completed": [
        "[kuhm,pleet,d]",
        "KMPLTT"
    ],
    "completely": [
        "[kuhm,pleet,ly]",
        "KMPLTL"
    ],
    "complex": [
        "[adjective]",
        "KMPLKS"
    ],
    "complexion": [
        "['kuhm', 'plek', 'shuhn']",
        "KMPLKSN"
    ],
    "complicated": [
        "['kom', 'pli', 'key', 'tid']",
        "KMPLKTT"
    ],
    "compliment": [
        "[nounkom,pluh,muhnt]",
        "KMPLMNT"
    ],
    "complimenting": [
        "[nounkom,pluh,muhnt,ing]",
        "KMPLMNTNK"
    ],
    "compliments": [
        "[nounkom,pluh,muhnt,s]",
        "KMPLMNTS"
    ],
    "composure": [
        "[kuhm,poh,zher]",
        "KMPSR"
    ],
    "compound": [
        "[adjectivekom,pound]",
        "KMPNT"
    ],
    "comprehend": [
        "['kom', 'pri', 'hend']",
        "KMPRHNT"
    ],
    "compromise": [
        "[kom,pruh,mahyz]",
        "KMPRMS"
    ],
    "compton": [
        "['komp', 'tuhn']",
        "KMPTN"
    ],
    "computer": [
        "['kuhm', 'pyoo', 'ter']",
        "KMPTR"
    ],
    "computers": [
        "['kuhm', 'pyoo', 'ter', 's']",
        "KMPTRS"
    ],
    "comrades": [
        "[kom,rad,s]",
        "KMRTS"
    ],
    "con": [
        "['kon']",
        "KN"
    ],
    "conceal": [
        "[kuhn,seel]",
        "KNSL"
    ],
    "concealed": [
        "[kuhn,seel,ed]",
        "KNSLT"
    ],
    "conceited": [
        "['kuhn', 'see', 'tid']",
        "KNSTT"
    ],
    "conceive": [
        "[kuhn,seev]",
        "KNSF"
    ],
    "conceived": [
        "[kuhn,seev,d]",
        "KNSFT"
    ],
    "concentrate": [
        "[kon,suhn,treyt]",
        "KNSNTRT"
    ],
    "concentration": [
        "['kon', 'suhn', 'trey', 'shuhn']",
        "KNSNTRXN"
    ],
    "concept": [
        "[kon,sept]",
        "KNSPT"
    ],
    "conception": [
        "[kuhn,sep,shuhn]",
        "KNSPXN"
    ],
    "concern": [
        "['kuhn', 'surn']",
        "KNSRN"
    ],
    "concerned": [
        "['kuhn', 'surnd']",
        "KNSRNT"
    ],
    "concert": [
        "['noun']",
        "KNSRT"
    ],
    "concerts": [
        "[noun,s]",
        "KNSRTS"
    ],
    "conclusion": [
        "[kuhn,kloo,zhuhn]",
        "KNKLSN"
    ],
    "concord": [
        "[kon,kawrd]",
        "KNKRT"
    ],
    "concrete": [
        "['kon', 'kreet']",
        "KNKRT"
    ],
    "concur": [
        "[kuhn,kur]",
        "KNKR"
    ],
    "concussion": [
        "['kuhn', 'kuhsh', 'uhn']",
        "KNKSN"
    ],
    "condition": [
        "[kuhn,dish,uhn]",
        "KNTXN"
    ],
    "condo": [
        "['kon', 'doh']",
        "KNT"
    ],
    "condom": [
        "['kon', 'duhm']",
        "KNTM"
    ],
    "condoms": [
        "['kon', 'duhm', 's']",
        "KNTMS"
    ],
    "condone": [
        "[kuhn,dohn]",
        "KNTN"
    ],
    "condos": [
        "['kon', 'doh', 's']",
        "KNTS"
    ],
    "conduct": [
        "['nounkon', 'duhkt']",
        "KNTKT"
    ],
    "cone": [
        "['kohn']",
        "KN"
    ],
    "confess": [
        "['kuhn', 'fes']",
        "KNFS"
    ],
    "confessing": [
        "[kuhn,fes,ing]",
        "KNFSNK"
    ],
    "confession": [
        "[kuhn,fesh,uhn]",
        "KNFSN"
    ],
    "confessions": [
        "['kuhn', 'fesh', 'uhn', 's']",
        "KNFSNS"
    ],
    "confetti": [
        "['kuhn', 'fet', 'eefor1']",
        "KNFT"
    ],
    "confidence": [
        "['kon', 'fi', 'duhns']",
        "KNFTNS"
    ],
    "confident": [
        "['kon', 'fi', 'duhnt']",
        "KNFTNT"
    ],
    "confidential": [
        "['kon', 'fi', 'den', 'shuhl']",
        "KNFTNXL"
    ],
    "confined": [
        "['kuhn', 'fahynd']",
        "KNFNT"
    ],
    "confirm": [
        "[kuhn,furm]",
        "KNFRM"
    ],
    "confirmed": [
        "[kuhn,furmd]",
        "KNFRMT"
    ],
    "confiscated": [
        "['verbkon', 'fuh', 'skeyt', 'd']",
        "KNFSKTT"
    ],
    "conflict": [
        "[verbkuhn,flikt]",
        "KNFLKT"
    ],
    "confront": [
        "[kuhn,fruhnt]",
        "KNFRNT"
    ],
    "confrontation": [
        "['kon', 'fruhn', 'tey', 'shuhn']",
        "KNFRNTXN"
    ],
    "confuse": [
        "['kuhn', 'fyooz']",
        "KNFS"
    ],
    "confused": [
        "['kuhn', 'fyooz', 'd']",
        "KNFST"
    ],
    "confusing": [
        "[kuhn,fyoo,zing]",
        "KNFSNK"
    ],
    "confusion": [
        "['kuhn', 'fyoo', 'zhuhn']",
        "KNFSN"
    ],
    "congratulations": [
        "['kuhn', 'grach', 'uh', 'ley', 'shuhnor', 's']",
        "KNKRTLXNS"
    ],
    "congregation": [
        "[kong,gri,gey,shuhn]",
        "KNKRKXN"
    ],
    "conjure": [
        "[kon,jer]",
        "KNJR"
    ],
    "connect": [
        "['kuh', 'nekt']",
        "KNKT"
    ],
    "connected": [
        "['kuh', 'nek', 'tid']",
        "KNKTT"
    ],
    "connecting": [
        "['kuh', 'nekt', 'ing']",
        "KNKTNK"
    ],
    "connection": [
        "['kuh', 'nek', 'shuhn']",
        "KNKXN"
    ],
    "connections": [
        "[kuh,nek,shuhn,s]",
        "KNKXNS"
    ],
    "connects": [
        "[kuh,nekt,s]",
        "KNKTS"
    ],
    "connoisseur": [
        "[kon,uh,sur]",
        "KNSR"
    ],
    "conquer": [
        "['kong', 'ker']",
        "KNKR"
    ],
    "conquered": [
        "[kong,ker,ed]",
        "KNKRT"
    ],
    "cons": [
        "['kon', 's']",
        "KNS"
    ],
    "conscience": [
        "[kon,shuhns]",
        "KNSNS"
    ],
    "conscious": [
        "['kon', 'shuhs']",
        "KNSS"
    ],
    "consequences": [
        "[kon,si,kwens,s]",
        "KNSKNSS"
    ],
    "consider": [
        "['kuhn', 'sid', 'er']",
        "KNSTR"
    ],
    "considered": [
        "[kuhn,sid,erd]",
        "KNSTRT"
    ],
    "considering": [
        "[kuhn,sid,er,ing]",
        "KNSTRNK"
    ],
    "consignment": [
        "[kuhn,sahyn,muhnt]",
        "KNSNMNT"
    ],
    "consist": [
        "[verbkuhn,sist]",
        "KNSST"
    ],
    "consistent": [
        "['kuhn', 'sis', 'tuhnt']",
        "KNSSTNT"
    ],
    "consistently": [
        "['kuhn', 'sis', 'tuhnt', 'ly']",
        "KNSSTNTL"
    ],
    "console": [
        "[kuhn,sohl]",
        "KNSL"
    ],
    "conspicuous": [
        "[kuhn,spik,yoo,uhs]",
        "KNSPKS"
    ],
    "conspiracy": [
        "[kuhn,spir,uh,see]",
        "KNSPRS"
    ],
    "constant": [
        "[kon,stuhnt]",
        "KNSTNT"
    ],
    "constantly": [
        "['kon', 'stuhnt', 'ly']",
        "KNSTNTL"
    ],
    "constipated": [
        "['kon', 'stuh', 'peyt', 'd']",
        "KNSTPTT"
    ],
    "construction": [
        "[kuhn,struhk,shuhn]",
        "KNSTRKXN"
    ],
    "contact": [
        "['kon', 'takt']",
        "KNTKT"
    ],
    "contacts": [
        "[kon,takt,s]",
        "KNTKTS"
    ],
    "contagious": [
        "['kuhn', 'tey', 'juhs']",
        "KNTJS"
    ],
    "contain": [
        "[kuhn,teyn]",
        "KNTN"
    ],
    "contemplate": [
        "[kon,tuhm,pleyt]",
        "KNTMPLT"
    ],
    "content": [
        "[kon,tent]",
        "KNTNT"
    ],
    "contest": [
        "[nounkon,test]",
        "KNTST"
    ],
    "continental": [
        "['kon', 'tn', 'en', 'tl']",
        "KNTNNTL"
    ],
    "continually": [
        "[kuhn,tin,yoo,uh,lee]",
        "KNTNL"
    ],
    "continue": [
        "['kuhn', 'tin', 'yoo']",
        "KNTN"
    ],
    "continued": [
        "[kuhn,tin,yood]",
        "KNTNT"
    ],
    "continues": [
        "[kuhn,tin,yoo,s]",
        "KNTNS"
    ],
    "contra": [
        "[kon,truh]",
        "KNTR"
    ],
    "contract": [
        "['noun']",
        "KNTRKT"
    ],
    "contractor": [
        "['kon', 'trak', 'ter']",
        "KNTRKTR"
    ],
    "contrast": [
        "[verbkuhn,trast]",
        "KNTRST"
    ],
    "contribution": [
        "['kon', 'truh', 'byoo', 'shuhn']",
        "KNTRPXN"
    ],
    "control": [
        "['kuhn', 'trohl']",
        "KNTRL"
    ],
    "controlled": [
        "['kuhn', 'trohld']",
        "KNTRLT"
    ],
    "controller": [
        "[kuhn,troh,ler]",
        "KNTRLR"
    ],
    "controlling": [
        "['kuhn', 'trohl', 'ling']",
        "KNTRLNK"
    ],
    "controversial": [
        "['kon', 'truh', 'vur', 'shuhl']",
        "KNTRFRSL"
    ],
    "controversy": [
        "['kon', 'truh', 'vur', 'see']",
        "KNTRFRS"
    ],
    "convenient": [
        "[kuhn,veen,yuhnt]",
        "KNFNNT"
    ],
    "convention": [
        "[kuhn,ven,shuhn]",
        "KNFNXN"
    ],
    "conversate": [
        "['kon', 'ver', 'seyt']",
        "KNFRST"
    ],
    "conversation": [
        "['kon', 'ver', 'sey', 'shuhn']",
        "KNFRSXN"
    ],
    "conversations": [
        "['kon', 'ver', 'sey', 'shuhn', 's']",
        "KNFRSXNS"
    ],
    "converse": [
        "['verbkuhn', 'vurs']",
        "KNFRS"
    ],
    "converted": [
        "[kuhn,vur,tid]",
        "KNFRTT"
    ],
    "convertible": [
        "['kuhn', 'vur', 'tuh', 'buhl']",
        "KNFRTPL"
    ],
    "convict": [
        "[verb]",
        "KNFKT"
    ],
    "convicted": [
        "['verb', 'ed']",
        "KNFKTT"
    ],
    "convicts": [
        "['verb', 's']",
        "KNFKTS"
    ],
    "convince": [
        "['kuhn', 'vins']",
        "KNFNS"
    ],
    "convinced": [
        "[kuhn,vins,d]",
        "KNFNST"
    ],
    "convincing": [
        "[kuhn,vin,sing]",
        "KNFNSNK"
    ],
    "convo": [
        "['kon', 'voh']",
        "KNF"
    ],
    "coo": [
        "[koo]",
        "K"
    ],
    "cook": [
        "['kook']",
        "KK"
    ],
    "cooked": [
        "['kook', 'ed']",
        "KKT"
    ],
    "cookie": [
        "['kook', 'ee']",
        "KK"
    ],
    "cookies": [
        "['kook', 'ee', 's']",
        "KKS"
    ],
    "cooking": [
        "['kook', 'ing']",
        "KKNK"
    ],
    "cooks": [
        "[kook,s]",
        "KKS"
    ],
    "cool": [
        "['kool']",
        "KL"
    ],
    "cooled": [
        "[kool,ed]",
        "KLT"
    ],
    "cooler": [
        "['koo', 'ler']",
        "KLR"
    ],
    "coolest": [
        "['kool', 'est']",
        "KLST"
    ],
    "cooling": [
        "['kool', 'ing']",
        "KLNK"
    ],
    "cooly": [
        "['koo', 'lee']",
        "KL"
    ],
    "coon": [
        "[koon]",
        "KN"
    ],
    "coop": [
        "['koop']",
        "KP"
    ],
    "cooper": [
        "['koo', 'per']",
        "KPR"
    ],
    "cooperate": [
        "[koh,op,uh,reyt]",
        "KPRT"
    ],
    "coordinate": [
        "['adjective']",
        "KRTNT"
    ],
    "cop": [
        "['kop']",
        "KP"
    ],
    "cop's": [
        "[kop,'s]",
        "KPPS"
    ],
    "cope": [
        "['kohp']",
        "KP"
    ],
    "coping": [
        "[koh,ping]",
        "KPNK"
    ],
    "copped": [
        "['kop', 'ped']",
        "KPT"
    ],
    "copper": [
        "['kop', 'er']",
        "KPR"
    ],
    "coppers": [
        "['kop', 'er', 's']",
        "KPRS"
    ],
    "copping": [
        "['kop', 'ing']",
        "KPNK"
    ],
    "cops": [
        "['kop', 's']",
        "KPS"
    ],
    "copy": [
        "['kop', 'ee']",
        "KP"
    ],
    "copying": [
        "['kop', 'ee', 'ing']",
        "KPNK"
    ],
    "cord": [
        "['kawrd']",
        "KRT"
    ],
    "cords": [
        "[kawrdz]",
        "KRTS"
    ],
    "core": [
        "[kawr]",
        "KR"
    ],
    "cork": [
        "['kawrk']",
        "KRK"
    ],
    "corks": [
        "[kawrk,s]",
        "KRKS"
    ],
    "corn": [
        "['kawrn']",
        "KRN"
    ],
    "corner": [
        "['kawr', 'ner']",
        "KRNR"
    ],
    "corners": [
        "['kawr', 'ner', 's']",
        "KRNRS"
    ],
    "corny": [
        "['kawr', 'nee']",
        "KRN"
    ],
    "corolla": [
        "[kuh,rol,uh]",
        "KRL"
    ],
    "coroner": [
        "['kawr', 'uh', 'ner']",
        "KRNR"
    ],
    "corporate": [
        "[kawr,per,it]",
        "KRPRT"
    ],
    "corpse": [
        "['kawrps']",
        "KRPS"
    ],
    "corpses": [
        "[kawrps,s]",
        "KRPSS"
    ],
    "corral": [
        "[kuh,ral]",
        "KRL"
    ],
    "correct": [
        "['kuh', 'rekt']",
        "KRKT"
    ],
    "correcting": [
        "[kuh,rekt,ing]",
        "KRKTNK"
    ],
    "correctional": [
        "[kuh,rek,shuh,nl]",
        "KRKXNL"
    ],
    "corridors": [
        "[kawr,i,der,s]",
        "KRTRS"
    ],
    "corrupt": [
        "[kuh,ruhpt]",
        "KRPT"
    ],
    "corrupted": [
        "[kuh,ruhpt,ed]",
        "KRPTT"
    ],
    "corruption": [
        "[kuh,ruhp,shuhn]",
        "KRPXN"
    ],
    "corse": [
        "[kawrs]",
        "KRS"
    ],
    "corvette": [
        "['kawr', 'vet']",
        "KRFT"
    ],
    "cos": [
        "['kos']",
        "KS"
    ],
    "cosign": [
        "['koh', 'sahyn']",
        "KSN"
    ],
    "cosigning": [
        "[koh,sahyn,ing]",
        "KSNNK"
    ],
    "cost": [
        "['kawst']",
        "KST"
    ],
    "costa": [
        "['kos', 'tuh']",
        "KST"
    ],
    "costing": [
        "['kaws', 'ting']",
        "KSTNK"
    ],
    "costs": [
        "['kawst', 's']",
        "KSTS"
    ],
    "costume": [
        "[nounkos,toom]",
        "KSTM"
    ],
    "cot": [
        "['kot']",
        "KT"
    ],
    "cotton": [
        "['kot', 'n']",
        "KTN"
    ],
    "couch": [
        "['kouchorfor6']",
        "KX"
    ],
    "couches": [
        "['kouchorfor6', 'es']",
        "KXS"
    ],
    "cougar": [
        "['koo', 'ger']",
        "KKR"
    ],
    "cougars": [
        "['koo', 'ger', 's']",
        "KKRS"
    ],
    "cough": [
        "['kawf']",
        "KF"
    ],
    "coughing": [
        "['kawf', 'ing']",
        "KFNK"
    ],
    "could": [
        "['kood']",
        "KLT"
    ],
    "could've": [
        [
            "kood",
            "ahv"
        ],
        "KLTTF"
    ],
    "couldn't": [
        "['kood', 'nt']",
        "KLTNNT"
    ],
    "counseling": [
        "['koun', 'suh', 'ling']",
        "KNSLNK"
    ],
    "counselor": [
        "[koun,suh,ler]",
        "KNSLR"
    ],
    "count": [
        "['kount']",
        "KNT"
    ],
    "countdown": [
        "[kount,doun]",
        "KNTN"
    ],
    "counted": [
        "['kount', 'ed']",
        "KNTT"
    ],
    "counter": [
        "['koun', 'ter']",
        "KNTR"
    ],
    "counterfeit": [
        "['koun', 'ter', 'fit']",
        "KNTRFT"
    ],
    "counting": [
        "['kount', 'ing']",
        "KNTNK"
    ],
    "country": [
        "['kuhn', 'tree']",
        "KNTR"
    ],
    "counts": [
        "['kount', 's']",
        "KNTS"
    ],
    "county": [
        "['koun', 'tee']",
        "KNT"
    ],
    "coupe": [
        "['koop']",
        "KP"
    ],
    "coupes": [
        "['koop', 's']",
        "KPS"
    ],
    "couple": [
        "['kuhp', 'uhl']",
        "KPL"
    ],
    "coupon": [
        "[koo,pon]",
        "KPN"
    ],
    "coups": [
        "['koo', 's']",
        "KPS"
    ],
    "courage": [
        "[kur,ij]",
        "KRJ"
    ],
    "courageous": [
        "[kuh,rey,juhs]",
        "KRJS"
    ],
    "course": [
        "['kawrs']",
        "KRS"
    ],
    "courses": [
        "[kawrs,s]",
        "KRSS"
    ],
    "court": [
        "['kawrt']",
        "KRT"
    ],
    "courtesy": [
        "[kur,tuh,seeorfor5]",
        "KRTS"
    ],
    "courthouse": [
        "['kawrt', 'hous']",
        "KR0S"
    ],
    "courtroom": [
        "[kawrt,room]",
        "KRTRM"
    ],
    "courts": [
        "['kawrt', 's']",
        "KRTS"
    ],
    "courtside": [
        "['kawrt', 'sahyd']",
        "KRTST"
    ],
    "cousin": [
        "['kuhz', 'uhn']",
        "KSN"
    ],
    "cousin's": [
        "[kuhz,uhn,'s]",
        "KSNNS"
    ],
    "cousins": [
        "['kuhz', 'uhn', 's']",
        "KSNS"
    ],
    "couture": [
        "['koo', 'toor']",
        "KTR"
    ],
    "cover": [
        "['kuhv', 'er']",
        "KFR"
    ],
    "covered": [
        "['kuhv', 'er', 'ed']",
        "KFRT"
    ],
    "covering": [
        "[kuhv,er,ing]",
        "KFRNK"
    ],
    "covers": [
        "['kuhv', 'er', 's']",
        "KFRS"
    ],
    "cow": [
        "['kou']",
        "K"
    ],
    "cowabunga": [
        "['kou', 'uh', 'buhng', 'guh']",
        "KPNK"
    ],
    "coward": [
        "['kou', 'erd']",
        "KRT"
    ],
    "cowards": [
        "[kou,erd,s]",
        "KRTS"
    ],
    "cowboy": [
        "[kou,boi]",
        "KP"
    ],
    "cowboys": [
        "['kou', 'boi', 's']",
        "KPS"
    ],
    "cowgirl": [
        "['kou', 'gurl']",
        "KJRL"
    ],
    "cows": [
        "[kou,s]",
        "KS"
    ],
    "cozy": [
        "['koh', 'zee']",
        "KS"
    ],
    "cpr": [
        "['sp', 'r']",
        "KPR"
    ],
    "cr": [
        "['krm', 'm']",
        "KR"
    ],
    "crab": [
        "['krab']",
        "KRP"
    ],
    "crabs": [
        "['krab', 's']",
        "KRPS"
    ],
    "crack": [
        "['krak']",
        "KRK"
    ],
    "cracked": [
        "['krakt']",
        "KRKT"
    ],
    "cracker": [
        "['krak', 'er']",
        "KRKR"
    ],
    "crackers": [
        "['krak', 'er', 's']",
        "KRKRS"
    ],
    "cracking": [
        "['krak', 'ing']",
        "KRKNK"
    ],
    "cracks": [
        "['krak', 's']",
        "KRKS"
    ],
    "cradle": [
        "[kreyd,l]",
        "KRTL"
    ],
    "craft": [
        "['kraft']",
        "KRFT"
    ],
    "cram": [
        "['kram']",
        "KRM"
    ],
    "cramp": [
        "['kramp']",
        "KRMP"
    ],
    "cramped": [
        "['krampt']",
        "KRMPT"
    ],
    "cranberry": [
        "['kran', 'ber', 'ee']",
        "KRNPR"
    ],
    "cranium": [
        "[krey,nee,uhm]",
        "KRNM"
    ],
    "crank": [
        "['krangk']",
        "KRNK"
    ],
    "cranking": [
        "['krangk', 'ing']",
        "KRNKNK"
    ],
    "cranky": [
        "[krang,kee]",
        "KRNK"
    ],
    "crap": [
        "['krap']",
        "KRP"
    ],
    "crappy": [
        "[krap,ee]",
        "KRP"
    ],
    "craps": [
        "['kraps']",
        "KRPS"
    ],
    "crash": [
        "['krash']",
        "KRX"
    ],
    "crashed": [
        "['krash', 'ed']",
        "KRXT"
    ],
    "crashing": [
        "['krash', 'ing']",
        "KRXNK"
    ],
    "crate": [
        "[kreyt]",
        "KRT"
    ],
    "craters": [
        "['krey', 'ter', 's']",
        "KRTRS"
    ],
    "crave": [
        "['kreyv']",
        "KRF"
    ],
    "craving": [
        "['krey', 'ving']",
        "KRFNK"
    ],
    "crawl": [
        "['krawl']",
        "KRL"
    ],
    "crawling": [
        "['krawl', 'ing']",
        "KRLNK"
    ],
    "craze": [
        "[kreyz]",
        "KRS"
    ],
    "crazy": [
        "['krey', 'zee']",
        "KRS"
    ],
    "cream": [
        "['kreem']",
        "KRM"
    ],
    "crease": [
        "[krees]",
        "KRS"
    ],
    "creases": [
        "[krees,s]",
        "KRSS"
    ],
    "create": [
        "['kree', 'eyt']",
        "KRT"
    ],
    "created": [
        "['kree', 'eyt', 'd']",
        "KRTT"
    ],
    "creatine": [
        "[kree,uh,teen]",
        "KRTN"
    ],
    "creation": [
        "[kree,ey,shuhn]",
        "KRXN"
    ],
    "creative": [
        "[kree,ey,tiv]",
        "KRTF"
    ],
    "creator": [
        "[kree,ey,ter]",
        "KRTR"
    ],
    "creature": [
        "['kree', 'cher']",
        "KRTR"
    ],
    "cred": [
        "['kred']",
        "KRT"
    ],
    "credentials": [
        "['kri', 'den', 'shuhl', 's']",
        "KRTNXLS"
    ],
    "credit": [
        "['kred', 'it']",
        "KRTT"
    ],
    "credits": [
        "[kred,it,s]",
        "KRTTS"
    ],
    "creed": [
        "['kreed']",
        "KRT"
    ],
    "creek": [
        "['kreek']",
        "KRK"
    ],
    "creep": [
        "['kreep']",
        "KRP"
    ],
    "creeped": [
        "[kreep,ed]",
        "KRPT"
    ],
    "creeper": [
        "[kree,per]",
        "KRPR"
    ],
    "creeping": [
        "['kree', 'ping']",
        "KRPNK"
    ],
    "cremate": [
        "[kree,meyt]",
        "KRMT"
    ],
    "creole": [
        "['kree', 'ohl']",
        "KRL"
    ],
    "crept": [
        "[krept]",
        "KRPT"
    ],
    "crescent": [
        "['kres', 'uhnt']",
        "KRSNT"
    ],
    "crest": [
        "['krest']",
        "KRST"
    ],
    "crew": [
        "['kroo']",
        "KR"
    ],
    "crew's": [
        "[kroo,'s]",
        "KRS"
    ],
    "crews": [
        "['kroo', 's']",
        "KRS"
    ],
    "crib": [
        "['krib']",
        "KRP"
    ],
    "cribs": [
        "['krib', 's']",
        "KRPS"
    ],
    "cried": [
        "['krahyd']",
        "KRT"
    ],
    "crime": [
        "['krahym']",
        "KRM"
    ],
    "crimes": [
        "['krahym', 's']",
        "KRMS"
    ],
    "criminal": [
        "['krim', 'uh', 'nl']",
        "KRMNL"
    ],
    "criminals": [
        "['krim', 'uh', 'nl', 's']",
        "KRMNLS"
    ],
    "crip": [
        "['krip']",
        "KRP"
    ],
    "crips": [
        "['krip', 's']",
        "KRPS"
    ],
    "crisis": [
        "['krahy', 'sis']",
        "KRSS"
    ],
    "crisp": [
        "[krisp]",
        "KRSP"
    ],
    "crispy": [
        "[kris,pee]",
        "KRSP"
    ],
    "critic": [
        "['krit', 'ik']",
        "KRTK"
    ],
    "critical": [
        "[krit,i,kuhl]",
        "KRTKL"
    ],
    "criticize": [
        "[krit,uh,sahyz]",
        "KRTSS"
    ],
    "critics": [
        "[krit,ik,s]",
        "KRTKS"
    ],
    "critique": [
        "[kri,teek]",
        "KRTK"
    ],
    "crocodile": [
        "['krok', 'uh', 'dahyl']",
        "KRKTL"
    ],
    "crook": [
        "['krook']",
        "KRK"
    ],
    "crooked": [
        "['krook', 'idfor14']",
        "KRKT"
    ],
    "crooks": [
        "['krook', 's']",
        "KRKS"
    ],
    "crop": [
        "['krop']",
        "KRP"
    ],
    "cross": [
        "['kraws']",
        "KRS"
    ],
    "crossed": [
        "['krawst']",
        "KRST"
    ],
    "crosses": [
        "['kraws', 'es']",
        "KRSS"
    ],
    "crossing": [
        "['kraw', 'sing']",
        "KRSNK"
    ],
    "crossover": [
        "['kraws', 'oh', 'ver']",
        "KRSFR"
    ],
    "crossroads": [
        "['kraws', 'rohd', 's']",
        "KRSRTS"
    ],
    "crotch": [
        "[kroch]",
        "KRX"
    ],
    "crow": [
        "[kroh]",
        "KR"
    ],
    "crowbar": [
        "['kroh', 'bahr']",
        "KRPR"
    ],
    "crowd": [
        "['kroud']",
        "KRT"
    ],
    "crowded": [
        "[krou,did]",
        "KRTT"
    ],
    "crowding": [
        "[kroud,ing]",
        "KRTNK"
    ],
    "crowds": [
        "[kroud,s]",
        "KRTS"
    ],
    "crown": [
        "['kroun']",
        "KRN"
    ],
    "crowned": [
        "[kround]",
        "KRNT"
    ],
    "crowns": [
        "[kroun,s]",
        "KRNS"
    ],
    "crows": [
        "['kroh', 's']",
        "KRS"
    ],
    "crucial": [
        "['kroo', 'shuhl']",
        "KRSL"
    ],
    "crucifix": [
        "['kroo', 'suh', 'fiks']",
        "KRSFKS"
    ],
    "crucify": [
        "['kroo', 'suh', 'fahy']",
        "KRSF"
    ],
    "cruel": [
        "['kroo', 'uhl']",
        "KRL"
    ],
    "cruise": [
        "['krooz']",
        "KRS"
    ],
    "cruiser": [
        "[kroo,zer]",
        "KRSR"
    ],
    "crumb": [
        "['kruhm']",
        "KRMP"
    ],
    "crumble": [
        "['kruhm', 'buhl']",
        "KRMPL"
    ],
    "crumbs": [
        "['kruhm', 's']",
        "KRMPS"
    ],
    "crunch": [
        "['kruhnch']",
        "KRNX"
    ],
    "crus": [
        "[kruhs]",
        "KRS"
    ],
    "crush": [
        "[kruhsh]",
        "KRX"
    ],
    "crushed": [
        "['kruhsh', 'ed']",
        "KRXT"
    ],
    "crushers": [
        "[kruhsh,ers]",
        "KRXRS"
    ],
    "crushing": [
        "[kruhsh,ing]",
        "KRXNK"
    ],
    "crust": [
        "['kruhst']",
        "KRST"
    ],
    "crutches": [
        "['kruhch', 'es']",
        "KRXS"
    ],
    "cry": [
        "['krahy']",
        "KR"
    ],
    "crying": [
        "['krahy', 'ing']",
        "KRNK"
    ],
    "crystal": [
        "['kris', 'tl']",
        "KRSTL"
    ],
    "crystals": [
        "[kris,tl,s]",
        "KRSTLS"
    ],
    "cs": [
        "['see']",
        "KS"
    ],
    "cub": [
        "[kuhb]",
        "KP"
    ],
    "cuba": [
        "['kyoo', 'buh']",
        "KP"
    ],
    "cuban": [
        "['kyoo', 'buh', 'n']",
        "KPN"
    ],
    "cubans": [
        "[kyoo,buh,ns]",
        "KPNS"
    ],
    "cube": [
        "['kyoob']",
        "KP"
    ],
    "cubes": [
        "[kyoob,s]",
        "KPS"
    ],
    "cubicle": [
        "['kyoo', 'bi', 'kuhl']",
        "KPKL"
    ],
    "cubs": [
        "[kuhb,s]",
        "KPS"
    ],
    "cuckoo": [
        "['koo', 'koo']",
        "KK"
    ],
    "cud": [
        "[kuhd]",
        "KT"
    ],
    "cuddle": [
        "['kuhd', 'l']",
        "KTL"
    ],
    "cuddy": [
        "['kuhd', 'ee']",
        "KT"
    ],
    "cue": [
        "[kyoo]",
        "K"
    ],
    "cuff": [
        "['kuhf']",
        "KF"
    ],
    "cuffed": [
        "['kuhf', 'ed']",
        "KFT"
    ],
    "cuffing": [
        "['kuhf', 'ing']",
        "KFNK"
    ],
    "cuffs": [
        "['kuhf', 's']",
        "KFS"
    ],
    "cuisine": [
        "['kwi', 'zeen']",
        "KSN"
    ],
    "culinary": [
        "[kyoo,luh,ner,ee]",
        "KLNR"
    ],
    "culprit": [
        "[kuhl,prit]",
        "KLPRT"
    ],
    "cult": [
        "[kuhlt]",
        "KLT"
    ],
    "culture": [
        "['kuhl', 'cher']",
        "KLTR"
    ],
    "cum": [
        "['koom']",
        "KM"
    ],
    "cumin": [
        "[kuhm,uhn]",
        "KMN"
    ],
    "cunt": [
        "[kuhnt]",
        "KNT"
    ],
    "cup": [
        "['kuhp']",
        "KP"
    ],
    "cupboard": [
        "['kuhb', 'erd']",
        "KPRT"
    ],
    "cupid": [
        "['kyoo', 'pid']",
        "KPT"
    ],
    "cupped": [
        "[kuhpt]",
        "KPT"
    ],
    "cupping": [
        "['kuhp', 'ing']",
        "KPNK"
    ],
    "cups": [
        "['kuhp', 's']",
        "KPS"
    ],
    "curb": [
        "['kurb']",
        "KRP"
    ],
    "curbs": [
        "[kurb,s]",
        "KRPS"
    ],
    "cure": [
        "['kyoor']",
        "KR"
    ],
    "curfew": [
        "['kur', 'fyoo']",
        "KRF"
    ],
    "curiosity": [
        "[kyoor,ee,os,i,tee]",
        "KRST"
    ],
    "curious": [
        "['kyoor', 'ee', 'uhs']",
        "KRS"
    ],
    "curl": [
        "['kurl']",
        "KRL"
    ],
    "curls": [
        "['kurl', 's']",
        "KRLS"
    ],
    "curly": [
        "['kur', 'lee']",
        "KRL"
    ],
    "currency": [
        "['kur', 'uhn', 'see']",
        "KRNS"
    ],
    "current": [
        "['kur', 'uhnt']",
        "KRNT"
    ],
    "currently": [
        "[kur,uhnt,lee]",
        "KRNTL"
    ],
    "curry": [
        "['kur', 'ee']",
        "KR"
    ],
    "curse": [
        "['kurs']",
        "KRS"
    ],
    "cursed": [
        "['kur', 'sid']",
        "KRST"
    ],
    "curses": [
        "['kurs', 's']",
        "KRSS"
    ],
    "cursive": [
        "[kur,siv]",
        "KRSF"
    ],
    "curtain": [
        "['kur', 'tn']",
        "KRTN"
    ],
    "curtains": [
        "['kur', 'tn', 's']",
        "KRTNS"
    ],
    "curtis": [
        "['kur', 'tis']",
        "KRTS"
    ],
    "curve": [
        "['kurv']",
        "KRF"
    ],
    "curved": [
        "['kurv', 'd']",
        "KRFT"
    ],
    "curves": [
        "[kurv,s]",
        "KRFS"
    ],
    "curvy": [
        "['kur', 'vee']",
        "KRF"
    ],
    "cushion": [
        "[koosh,uhn]",
        "KXN"
    ],
    "cuss": [
        "['kuhs']",
        "KS"
    ],
    "cussing": [
        "[kuhs,ing]",
        "KSNK"
    ],
    "custody": [
        "['kuhs', 'tuh', 'dee']",
        "KSTT"
    ],
    "custom": [
        "['kuhs', 'tuhm']",
        "KSTM"
    ],
    "customer": [
        "[kuhs,tuh,mer]",
        "KSTMR"
    ],
    "customers": [
        "['kuhs', 'tuh', 'mer', 's']",
        "KSTMRS"
    ],
    "customs": [
        "[kuhs,tuhm,s]",
        "KSTMS"
    ],
    "cut": [
        "['kuht']",
        "KT"
    ],
    "cute": [
        "['kyoot']",
        "KT"
    ],
    "cuter": [
        "[kyoot,r]",
        "KTR"
    ],
    "cutest": [
        "[kyoot,st]",
        "KTST"
    ],
    "cutie": [
        "['kyoo', 'tee']",
        "KT"
    ],
    "cutlass": [
        "['kuht', 'luhs']",
        "KTLS"
    ],
    "cutler": [
        "['kuht', 'ler']",
        "KTLR"
    ],
    "cuts": [
        "['kuht', 's']",
        "KTS"
    ],
    "cutter": [
        "[kuht,er]",
        "KTR"
    ],
    "cutthroat": [
        "['kuht', 'throht']",
        "K0RT"
    ],
    "cutting": [
        "['kuht', 'ing']",
        "KTNK"
    ],
    "cycle": [
        "['sahy', 'kuhl']",
        "SKL"
    ],
    "cyclone": [
        "[sahy,klohn]",
        "SKLN"
    ],
    "cyclops": [
        "[sahy,klops]",
        "SKLPS"
    ],
    "cypher": [
        "[sahy,fer]",
        "SFR"
    ],
    "cyrus": [
        "['sahy', 'ruhs']",
        "SRS"
    ],
    "c\u00e9line": [
        "['sey', 'leen']",
        "SLN"
    ],
    "d": [
        "['dee', '']",
        "T"
    ],
    "d'oh": [
        "[doh]",
        "TT"
    ],
    "d'uss\u00e9": [
        [
            "dou",
            "sey"
        ],
        "TTS"
    ],
    "dab": [
        "['dab']",
        "TP"
    ],
    "dabbed": [
        "['dab', 'bed']",
        "TPT"
    ],
    "dabbing": [
        "['dab', 'ing']",
        "TPNK"
    ],
    "dad": [
        "['dad']",
        "TT"
    ],
    "dad's": [
        "[dad,'s]",
        "TTTS"
    ],
    "dada": [
        "['dah', 'dah']",
        "TT"
    ],
    "daddy": [
        "['dad', 'ee']",
        "TT"
    ],
    "daddy's": [
        "['dad', 'ee', \"'s\"]",
        "TTS"
    ],
    "dads": [
        "[dad,s]",
        "TTS"
    ],
    "dagger": [
        "['dag', 'er']",
        "TKR"
    ],
    "daily": [
        "['dey', 'lee']",
        "TL"
    ],
    "daiquiri": [
        "[dahy,kuh,ree]",
        "TKR"
    ],
    "dairy": [
        "['dair', 'ee']",
        "TR"
    ],
    "daisy": [
        "['dey', 'zee']",
        "TS"
    ],
    "dakota": [
        "['duh', 'koh', 'tuh']",
        "TKT"
    ],
    "dale": [
        "[deyl]",
        "TL"
    ],
    "dallas": [
        "['dal', 'uhs']",
        "TLS"
    ],
    "dam": [
        "['dam']",
        "TM"
    ],
    "damage": [
        "['dam', 'ij']",
        "TMJ"
    ],
    "damaged": [
        "['dam', 'ij', 'd']",
        "TMJT"
    ],
    "damaging": [
        "[dam,i,jing]",
        "TMJNK"
    ],
    "dame": [
        "['deym']",
        "TM"
    ],
    "dames": [
        "['deym', 's']",
        "TMS"
    ],
    "damn": [
        "['dam']",
        "TMN"
    ],
    "damned": [
        "['damd']",
        "TMNT"
    ],
    "damon": [
        "[dey,muhn]",
        "TMN"
    ],
    "damp": [
        "[damp]",
        "TMP"
    ],
    "dance": [
        "['dans']",
        "TNS"
    ],
    "danced": [
        "[dans,d]",
        "TNST"
    ],
    "dancer": [
        "['dan', 'ser']",
        "TNSR"
    ],
    "dancers": [
        "['dan', 'ser', 's']",
        "TNSRS"
    ],
    "dances": [
        "[dans,s]",
        "TNSS"
    ],
    "dandruff": [
        "['dan', 'druhf']",
        "TNTRF"
    ],
    "dandy": [
        "[dan,dee]",
        "TNT"
    ],
    "dang": [
        "['dang']",
        "TNK"
    ],
    "danger": [
        "['deyn', 'jer']",
        "TNJR"
    ],
    "dangerous": [
        "['deyn', 'jer', 'uhs']",
        "TNJRS"
    ],
    "dangle": [
        "[dang,guhl]",
        "TNKL"
    ],
    "dangled": [
        "[dang,guhl,d]",
        "TNKLT"
    ],
    "daniel": [
        "['dan', 'yuhl']",
        "TNL"
    ],
    "daniels": [
        "[dan,yuhlz]",
        "TNLS"
    ],
    "dank": [
        "['dangk']",
        "TNK"
    ],
    "danny": [
        "['dan', 'ee']",
        "TN"
    ],
    "dante": [
        "[dan,tee]",
        "TNT"
    ],
    "dapper": [
        "[dap,er]",
        "TPR"
    ],
    "dare": [
        "['dair']",
        "TR"
    ],
    "dark": [
        "['dahrk']",
        "TRK"
    ],
    "darken": [
        "[dahr,kuhn]",
        "TRKN"
    ],
    "darker": [
        "[dahrk,er]",
        "TRKR"
    ],
    "darkest": [
        "['dahrk', 'est']",
        "TRKST"
    ],
    "darkness": [
        "['dahrk', 'nis']",
        "TRKNS"
    ],
    "darling": [
        "['dahr', 'ling']",
        "TRLNK"
    ],
    "dart": [
        "[dahrt]",
        "TRT"
    ],
    "darts": [
        "['dahrt', 's']",
        "TRTS"
    ],
    "das": [
        "[das]",
        "TS"
    ],
    "dash": [
        "['dash']",
        "TX"
    ],
    "dashboard": [
        "['dash', 'bawrd']",
        "TXPRT"
    ],
    "dashing": [
        "['dash', 'ing']",
        "TXNK"
    ],
    "dat": [
        "['dij', 'i', 'tlaw', 'dee', 'oh', 'teyp', '']",
        "TT"
    ],
    "data": [
        "[dey,tuh]",
        "TT"
    ],
    "database": [
        "['dey', 'tuh', 'beys']",
        "TTPS"
    ],
    "date": [
        "['deyt']",
        "TT"
    ],
    "dated": [
        "['dey', 'tid']",
        "TTT"
    ],
    "dates": [
        "['deyt', 's']",
        "TTS"
    ],
    "dating": [
        [
            "dey",
            "ting"
        ],
        "TTNK"
    ],
    "daughter": [
        "['daw', 'ter']",
        "TTR"
    ],
    "daughter's": [
        "[daw,ter,'s]",
        "TTRRS"
    ],
    "daughters": [
        "['daw', 'ter', 's']",
        "TTRS"
    ],
    "david": [
        "['dey', 'vidfor1']",
        "TFT"
    ],
    "davis": [
        "['dey', 'vis']",
        "TFS"
    ],
    "dawn": [
        "['dawn']",
        "TN"
    ],
    "day": [
        "['dey']",
        "T"
    ],
    "day's": [
        "[dey,'s]",
        "TS"
    ],
    "daydream": [
        "[dey,dreem]",
        "TTRM"
    ],
    "daylight": [
        "['dey', 'lahyt']",
        "TLT"
    ],
    "days": [
        "['deyz']",
        "TS"
    ],
    "daytime": [
        "['dey', 'tahym']",
        "TTM"
    ],
    "daytons": [
        "[deyt,n,s]",
        "TTNS"
    ],
    "daze": [
        "[deyz]",
        "TS"
    ],
    "de": [
        "['duh']",
        "T"
    ],
    "deacon": [
        "['dee', 'kuhn']",
        "TKN"
    ],
    "dead": [
        "['ded']",
        "TT"
    ],
    "deadbeat": [
        "[nounded,beet]",
        "TTPT"
    ],
    "deadline": [
        "[ded,lahyn]",
        "TTLN"
    ],
    "deadly": [
        "['ded', 'lee']",
        "TTL"
    ],
    "deaf": [
        "['def']",
        "TF"
    ],
    "deal": [
        "['deel']",
        "TL"
    ],
    "dealer": [
        "['dee', 'ler']",
        "TLR"
    ],
    "dealers": [
        "['dee', 'ler', 's']",
        "TLRS"
    ],
    "dealership": [
        "['dee', 'ler', 'ship']",
        "TLRXP"
    ],
    "dealing": [
        "['dee', 'ling']",
        "TLNK"
    ],
    "dealings": [
        "[dee,ling,s]",
        "TLNKS"
    ],
    "deals": [
        "['deel', 's']",
        "TLS"
    ],
    "dealt": [
        "['delt']",
        "TLT"
    ],
    "dean": [
        "['deen']",
        "TN"
    ],
    "dear": [
        "['deer']",
        "TR"
    ],
    "dearly": [
        "[deer,ly]",
        "TRL"
    ],
    "death": [
        "['deth']",
        "T0"
    ],
    "deaths": [
        "[deth,s]",
        "T0S"
    ],
    "debate": [
        "['dih', 'beyt']",
        "TPT"
    ],
    "debated": [
        "[dih,beyt,d]",
        "TPTT"
    ],
    "debit": [
        "['deb', 'it']",
        "TPT"
    ],
    "debris": [
        "[duh,bree]",
        "TPRS"
    ],
    "debt": [
        "['det']",
        "TPT"
    ],
    "debut": [
        "[dey,byoo]",
        "TPT"
    ],
    "decade": [
        "[dek,eyd]",
        "TKT"
    ],
    "decapitate": [
        "['dih', 'kap', 'i', 'teyt']",
        "TKPTT"
    ],
    "decatur": [
        "['dih', 'key', 'ter']",
        "TKTR"
    ],
    "decay": [
        "[dih,key]",
        "TK"
    ],
    "deceased": [
        "['dih', 'seest']",
        "TSST"
    ],
    "deceitful": [
        "[dih,seet,fuhl]",
        "TSTFL"
    ],
    "december": [
        "['dih', 'sem', 'ber']",
        "TSMPR"
    ],
    "decent": [
        "['dee', 'suhnt']",
        "TSNT"
    ],
    "deception": [
        "[dih,sep,shuhn]",
        "TSPXN"
    ],
    "decibels": [
        "[des,uh,bel,s]",
        "TSPLS"
    ],
    "decide": [
        "['dih', 'sahyd']",
        "TST"
    ],
    "decided": [
        "[dih,sahy,did]",
        "TSTT"
    ],
    "decimal": [
        "[des,uh,muhl]",
        "TSML"
    ],
    "decimals": [
        "['des', 'uh', 'muhl', 's']",
        "TSMLS"
    ],
    "decision": [
        "['dih', 'sizh', 'uhn']",
        "TSSN"
    ],
    "decisions": [
        "['dih', 'sizh', 'uhn', 's']",
        "TSSNS"
    ],
    "deck": [
        "['dek']",
        "TK"
    ],
    "declare": [
        "['dih', 'klair']",
        "TKLR"
    ],
    "decline": [
        "[dih,klahyn]",
        "TKLN"
    ],
    "declined": [
        "[dih,klahyn,d]",
        "TKLNT"
    ],
    "decorated": [
        "[dek,uh,rey,tid]",
        "TKRTT"
    ],
    "decoration": [
        "['dek', 'uh', 'rey', 'shuhn']",
        "TKRXN"
    ],
    "decoy": [
        "[noundee,koi]",
        "TK"
    ],
    "dedicate": [
        "['verbded', 'i', 'keyt']",
        "TTKT"
    ],
    "dedicated": [
        "[ded,i,key,tid]",
        "TTKTT"
    ],
    "dedication": [
        "[ded,i,key,shuhn]",
        "TTKXN"
    ],
    "deed": [
        "[deed]",
        "TT"
    ],
    "deep": [
        "['deep']",
        "TP"
    ],
    "deeper": [
        "['deep', 'er']",
        "TPR"
    ],
    "deepest": [
        "['deep', 'est']",
        "TPST"
    ],
    "deer": [
        "[deer]",
        "TR"
    ],
    "deere": [
        "[deer]",
        "TR"
    ],
    "deers": [
        "['deer', 's']",
        "TRS"
    ],
    "defeat": [
        "['dih', 'feet']",
        "TFT"
    ],
    "defeated": [
        "['dih', 'feet', 'ed']",
        "TFTT"
    ],
    "defend": [
        "['dih', 'fend']",
        "TFNT"
    ],
    "defendant": [
        "[dih,fen,duhntorespeciallyincourtfor1]",
        "TFNTNT"
    ],
    "defender": [
        "[dih,fend,er]",
        "TFNTR"
    ],
    "defending": [
        "['dih', 'fend', 'ing']",
        "TFNTNK"
    ],
    "defense": [
        "['dih', 'fensorespeciallyfor7']",
        "TFNS"
    ],
    "defiant": [
        "[dih,fahy,uhnt]",
        "TFNT"
    ],
    "define": [
        "[dih,fahyn]",
        "TFN"
    ],
    "defined": [
        "[dih,fahynd]",
        "TFNT"
    ],
    "definitely": [
        "[def,uh,nit,lee]",
        "TFNTL"
    ],
    "definition": [
        "['def', 'uh', 'nish', 'uhn']",
        "TFNXN"
    ],
    "deflate": [
        "[dih,fleyt]",
        "TFLT"
    ],
    "defrost": [
        "[dih,frawst]",
        "TFRST"
    ],
    "defying": [
        "[verbdih,fahy,ing]",
        "TFNK"
    ],
    "degree": [
        "['dih', 'gree']",
        "TKR"
    ],
    "degrees": [
        "['dih', 'gree', 's']",
        "TKRS"
    ],
    "delay": [
        "[dih,ley]",
        "TL"
    ],
    "delayed": [
        "[dih,leyd]",
        "TLT"
    ],
    "delete": [
        "['dih', 'leet']",
        "TLT"
    ],
    "deleted": [
        "[dih,leet,d]",
        "TLTT"
    ],
    "deli": [
        "[del,ee]",
        "TL"
    ],
    "delicate": [
        "['del', 'i', 'kit']",
        "TLKT"
    ],
    "delicious": [
        "['dih', 'lish', 'uhs']",
        "TLSS"
    ],
    "delight": [
        "[dih,lahyt]",
        "TLT"
    ],
    "delirious": [
        "['dih', 'leer', 'ee', 'uhs']",
        "TLRS"
    ],
    "deliver": [
        "[dih,liv,er]",
        "TLFR"
    ],
    "delivered": [
        "['dih', 'liv', 'er', 'ed']",
        "TLFRT"
    ],
    "delivery": [
        "[dih,liv,uh,ree]",
        "TLFR"
    ],
    "delta": [
        "[del,tuh]",
        "TLT"
    ],
    "demand": [
        "['dih', 'mand']",
        "TMNT"
    ],
    "demanded": [
        "['dih', 'mand', 'ed']",
        "TMNTT"
    ],
    "demanding": [
        "['dih', 'man', 'ding']",
        "TMNTNK"
    ],
    "demands": [
        "[dih,mand,s]",
        "TMNTS"
    ],
    "demeanor": [
        "[dih,mee,ner]",
        "TMNR"
    ],
    "demented": [
        "[dih,men,tid]",
        "TMNTT"
    ],
    "demise": [
        "[dih,mahyz]",
        "TMS"
    ],
    "demo": [
        "['dem', 'oh']",
        "TM"
    ],
    "democrat": [
        "['dem', 'uh', 'krat']",
        "TMKRT"
    ],
    "demolished": [
        "[dih,mol,ish,ed]",
        "TMLXT"
    ],
    "demon": [
        "['dee', 'muhn']",
        "TMN"
    ],
    "demonic": [
        "['dih', 'mon', 'ik']",
        "TMNK"
    ],
    "demons": [
        "['dee', 'muhn', 's']",
        "TMNS"
    ],
    "demonstration": [
        "[dem,uhn,strey,shuhn]",
        "TMNSTRXN"
    ],
    "den": [
        "['den']",
        "TN"
    ],
    "denial": [
        "['dih', 'nahy', 'uhl']",
        "TNL"
    ],
    "denim": [
        "['den', 'uhm']",
        "TNM"
    ],
    "dennis": [
        "['den', 'is']",
        "TNS"
    ],
    "denny's": [
        "['den', 'ee', \"'s\"]",
        "TNS"
    ],
    "dense": [
        "[dens]",
        "TNS"
    ],
    "dent": [
        "['dent']",
        "TNT"
    ],
    "dental": [
        "['den', 'tl']",
        "TNTL"
    ],
    "dentist": [
        "['den', 'tist']",
        "TNTST"
    ],
    "dentures": [
        "['den', 'cher', 's']",
        "TNTRS"
    ],
    "denver": [
        "[den,ver]",
        "TNFR"
    ],
    "deny": [
        "['dih', 'nahy']",
        "TN"
    ],
    "denying": [
        "['dih', 'nahy', 'ing']",
        "TNNK"
    ],
    "depart": [
        "['dih', 'pahrt']",
        "TPRT"
    ],
    "departed": [
        "[dih,pahr,tid]",
        "TPRTT"
    ],
    "department": [
        "['dih', 'pahrt', 'muhnt']",
        "TPRTMNT"
    ],
    "depend": [
        "['dih', 'pend']",
        "TPNT"
    ],
    "depended": [
        "[dih,pend,ed]",
        "TPNTT"
    ],
    "dependent": [
        "['dih', 'pen', 'duhnt']",
        "TPNTNT"
    ],
    "depending": [
        "['dih', 'pend', 'ing']",
        "TPNTNK"
    ],
    "depends": [
        "[dih,pend,s]",
        "TPNTS"
    ],
    "deport": [
        "[dih,pawrt]",
        "TPRT"
    ],
    "deposit": [
        "['dih', 'poz', 'it']",
        "TPST"
    ],
    "deposits": [
        "['dih', 'poz', 'it', 's']",
        "TPSTS"
    ],
    "depot": [
        "['dee', 'poh']",
        "TPT"
    ],
    "depressed": [
        "['dih', 'prest']",
        "TPRST"
    ],
    "depressing": [
        "[dih,pres,ing]",
        "TPRSNK"
    ],
    "depression": [
        "['dih', 'presh', 'uhn']",
        "TPRSN"
    ],
    "deprived": [
        "[dih,prahyvd]",
        "TPRFT"
    ],
    "depth": [
        "[depth]",
        "TP0"
    ],
    "derail": [
        "[dee,reyl]",
        "TRL"
    ],
    "deranged": [
        "[dih,reynjd]",
        "TRNJT"
    ],
    "derby": [
        "['dur', 'bee']",
        "TRP"
    ],
    "derrick": [
        "['der', 'ik']",
        "TRK"
    ],
    "des": [
        "['dey']",
        "TS"
    ],
    "descent": [
        "[dih,sent]",
        "TSNT"
    ],
    "describe": [
        "['dih', 'skrahyb']",
        "TSKP"
    ],
    "description": [
        "[dih,skrip,shuhn]",
        "TSKPXN"
    ],
    "desert": [
        "['dez', 'ert']",
        "TSRT"
    ],
    "deserted": [
        "[dih,zur,tid]",
        "TSRTT"
    ],
    "deserve": [
        "['dih', 'zurv']",
        "TSRF"
    ],
    "deserved": [
        "[dih,zurvd]",
        "TSRFT"
    ],
    "deserves": [
        "[dih,zurv,s]",
        "TSRFS"
    ],
    "design": [
        "[dih,zahyn]",
        "TSN"
    ],
    "designed": [
        "['dih', 'zahynd']",
        "TSNT"
    ],
    "designer": [
        "['dih', 'zahy', 'ner']",
        "TSNR"
    ],
    "designers": [
        "[dih,zahy,ner,s]",
        "TSNRS"
    ],
    "desire": [
        "['dih', 'zahyuhr']",
        "TSR"
    ],
    "desires": [
        "['dih', 'zahyuhr', 's']",
        "TSRS"
    ],
    "desk": [
        "[desk]",
        "TSK"
    ],
    "despair": [
        "[dih,spair]",
        "TSPR"
    ],
    "desperado": [
        "[des,puh,rah,doh]",
        "TSPRT"
    ],
    "desperate": [
        "['des', 'per', 'it']",
        "TSPRT"
    ],
    "despise": [
        "['dih', 'spahyz']",
        "TSPS"
    ],
    "despite": [
        "['dih', 'spahyt']",
        "TSPT"
    ],
    "dessert": [
        "['dih', 'zurt']",
        "TSRT"
    ],
    "destination": [
        "[des,tuh,ney,shuhn]",
        "TSTNXN"
    ],
    "destined": [
        "['des', 'tind']",
        "TSTNT"
    ],
    "destiny": [
        "['des', 'tuh', 'nee']",
        "TSTN"
    ],
    "destroy": [
        "['dih', 'stroi']",
        "TSTR"
    ],
    "destroyed": [
        "['dih', 'stroi', 'ed']",
        "TSTRT"
    ],
    "destruction": [
        "['dih', 'struhk', 'shuhn']",
        "TSTRKXN"
    ],
    "detail": [
        "['noundih', 'teyl']",
        "TTL"
    ],
    "details": [
        "[noundih,teyl,s]",
        "TTLS"
    ],
    "detectives": [
        "['dih', 'tek', 'tiv', 's']",
        "TTKTFS"
    ],
    "detector": [
        "['dih', 'tek', 'ter']",
        "TTKTR"
    ],
    "detention": [
        "[dih,ten,shuhn]",
        "TTNXN"
    ],
    "detergent": [
        "['dih', 'tur', 'juhnt']",
        "TTRJNT"
    ],
    "determination": [
        "[dih,tur,muh,ney,shuhn]",
        "TTRMNXN"
    ],
    "determine": [
        "[dih,tur,min]",
        "TTRMN"
    ],
    "determined": [
        "[dih,tur,mind]",
        "TTRMNT"
    ],
    "detonation": [
        "[det,n,ey,shuhn]",
        "TTNXN"
    ],
    "detour": [
        "[dee,toor]",
        "TTR"
    ],
    "detox": [
        "[noundee,toks]",
        "TTKS"
    ],
    "detrimental": [
        "['de', 'truh', 'men', 'tl']",
        "TTRMNTL"
    ],
    "detroit": [
        "['dih', 'troit']",
        "TTRT"
    ],
    "deuce": [
        "['doos']",
        "TS"
    ],
    "deuces": [
        "[doos,s]",
        "TSS"
    ],
    "develop": [
        "[dih,vel,uhp]",
        "TFLP"
    ],
    "developed": [
        "[dih,vel,uhp,ed]",
        "TFLPT"
    ],
    "device": [
        "[dih,vahys]",
        "TFS"
    ],
    "devil": [
        "['dev', 'uhl']",
        "TFL"
    ],
    "devil's": [
        "[dev,uhl,'s]",
        "TFLLS"
    ],
    "devilish": [
        "[dev,uh,lish]",
        "TFLX"
    ],
    "devils": [
        "[dev,uhl,s]",
        "TFLS"
    ],
    "devoted": [
        "['dih', 'voh', 'tid']",
        "TFTT"
    ],
    "devotion": [
        "[dih,voh,shuhn]",
        "TFXN"
    ],
    "devoured": [
        "[dih,vou,uhr,ed]",
        "TFRT"
    ],
    "dew": [
        "['doo']",
        "T"
    ],
    "di": [
        "['dee']",
        "T"
    ],
    "diablo": [
        "['dee', 'ah', 'bloh']",
        "TPL"
    ],
    "diagnosed": [
        "['dahy', 'uhg', 'nohs', 'd']",
        "TNST"
    ],
    "dial": [
        "['dahy', 'uhl']",
        "TL"
    ],
    "dialing": [
        "[dahy,uhl,ing]",
        "TLNK"
    ],
    "diamond": [
        "['dahy', 'muhnd']",
        "TMNT"
    ],
    "diamond's": [
        "[dahy,muhnd,'s]",
        "TMNTTS"
    ],
    "diamonds": [
        "['dahy', 'muhnd', 's']",
        "TMNTS"
    ],
    "diana": [
        "['dahy', 'an', 'uh']",
        "TN"
    ],
    "diaper": [
        "['dahy', 'per']",
        "TPR"
    ],
    "diapers": [
        "['dahy', 'per', 's']",
        "TPRS"
    ],
    "diarrhea": [
        "[dahy,uh,ree,uh]",
        "TR"
    ],
    "diary": [
        "[dahy,uh,ree]",
        "TR"
    ],
    "dice": [
        "['dahys']",
        "TS"
    ],
    "dices": [
        "['dahys', 's']",
        "TSS"
    ],
    "dick": [
        "['dik']",
        "TK"
    ],
    "dick's": [
        "[dik,'s]",
        "TKK"
    ],
    "dickies": [
        [
            "dik",
            "ees"
        ],
        "TKS"
    ],
    "dicks": [
        "['dik', 's']",
        "TKS"
    ],
    "dictionary": [
        "['dik', 'shuh', 'ner', 'ee']",
        "TKXNR"
    ],
    "did": [
        "['did']",
        "TT"
    ],
    "didn't": [
        "['did', 'nt']",
        "TTNNT"
    ],
    "die": [
        "['dahy']",
        "T"
    ],
    "died": [
        "['dahy', 'd']",
        "TT"
    ],
    "dieing": [
        "[dahy,ing]",
        "TNK"
    ],
    "dies": [
        "[dahyz]",
        "TS"
    ],
    "diesel": [
        "['dee', 'zuhl']",
        "TSL"
    ],
    "diet": [
        "['dahy', 'it']",
        "TT"
    ],
    "differ": [
        "[dif,er]",
        "TFR"
    ],
    "difference": [
        "['dif', 'er', 'uhns']",
        "TFRNS"
    ],
    "differences": [
        "[dif,er,uhns,s]",
        "TFRNSS"
    ],
    "different": [
        "['dif', 'er', 'uhnt']",
        "TFRNT"
    ],
    "differently": [
        "[dif,er,uhnt,ly]",
        "TFRNTL"
    ],
    "difficult": [
        "[dif,i,kuhlt]",
        "TFKLT"
    ],
    "dig": [
        "['dig']",
        "TK"
    ],
    "digest": [
        "['verbdih', 'jest']",
        "TJST"
    ],
    "digger": [
        "[dig,er]",
        "TKR"
    ],
    "diggers": [
        "[dig,er,s]",
        "TKRS"
    ],
    "digging": [
        "['dig', 'ging']",
        "TKNK"
    ],
    "diggy": [
        [
            "dig",
            "ee"
        ],
        "TK"
    ],
    "digit": [
        "[dij,it]",
        "TJT"
    ],
    "digital": [
        "['dij', 'i', 'tl']",
        "TJTL"
    ],
    "digits": [
        "['dij', 'it', 's']",
        "TJTS"
    ],
    "dignity": [
        "['dig', 'ni', 'tee']",
        "TNT"
    ],
    "dike": [
        "[dahyk]",
        "TK"
    ],
    "dikes": [
        "['dahyk', 's']",
        "TKS"
    ],
    "dildo": [
        "['dil', 'doh']",
        "TLT"
    ],
    "dilemma": [
        "[dih,lem,uh]",
        "TLM"
    ],
    "dill": [
        "['dil']",
        "TL"
    ],
    "dim": [
        "[dim]",
        "TM"
    ],
    "dime": [
        "['dahym']",
        "TM"
    ],
    "dimension": [
        "[dih,men,shuhn]",
        "TMNSN"
    ],
    "dimensions": [
        "[dih,men,shuhn,s]",
        "TMNSNS"
    ],
    "dimes": [
        "['dahym', 's']",
        "TMS"
    ],
    "diminish": [
        "['dih', 'min', 'ish']",
        "TMNX"
    ],
    "dimple": [
        "[dim,puhl]",
        "TMPL"
    ],
    "dimples": [
        "[dim,puhl,s]",
        "TMPLS"
    ],
    "dine": [
        "['dahyn']",
        "TN"
    ],
    "diner": [
        "['dahy', 'ner']",
        "TNR"
    ],
    "dinero": [
        "['dih', 'nair', 'oh']",
        "TNR"
    ],
    "ding": [
        "['ding']",
        "TNK"
    ],
    "dinner": [
        "['din', 'er']",
        "TNR"
    ],
    "dinners": [
        "['din', 'er', 's']",
        "TNRS"
    ],
    "dinosaur": [
        "['dahy', 'nuh', 'sawr']",
        "TNSR"
    ],
    "dior": [
        "['dee', 'awr']",
        "TR"
    ],
    "dip": [
        "['dip']",
        "TP"
    ],
    "diploma": [
        "[dih,ploh,muh]",
        "TPLM"
    ],
    "diplomas": [
        "[dih,ploh,muh,s]",
        "TPLMS"
    ],
    "dipped": [
        "['dip', 'ped']",
        "TPT"
    ],
    "dipper": [
        "[dip,er]",
        "TPR"
    ],
    "dipping": [
        "['dip', 'ping']",
        "TPNK"
    ],
    "dips": [
        "[dip,s]",
        "TPS"
    ],
    "dire": [
        "[dahyuhr]",
        "TR"
    ],
    "direct": [
        "['dih', 'rekt']",
        "TRKT"
    ],
    "directing": [
        "[dih,rekt,ing]",
        "TRKTNK"
    ],
    "direction": [
        "['dih', 'rek', 'shuhn']",
        "TRKXN"
    ],
    "directions": [
        "[dih,rek,shuhn,s]",
        "TRKXNS"
    ],
    "directly": [
        "[dih,rekt,lee]",
        "TRKTL"
    ],
    "director": [
        "[dih,rek,ter]",
        "TRKTR"
    ],
    "dirk": [
        "['durk']",
        "TRK"
    ],
    "dirt": [
        "['durt']",
        "TRT"
    ],
    "dirty": [
        "['dur', 'tee']",
        "TRT"
    ],
    "dis": [
        "['dees']",
        "TS"
    ],
    "disagree": [
        "['dis', 'uh', 'gree']",
        "TSKR"
    ],
    "disagreed": [
        "[dis,uh,gree,d]",
        "TSKRT"
    ],
    "disappear": [
        "['dis', 'uh', 'peer']",
        "TSPR"
    ],
    "disappeared": [
        "[dis,uh,peer,ed]",
        "TSPRT"
    ],
    "disappearing": [
        "[dis,uh,peer,ing]",
        "TSPRNK"
    ],
    "disappoint": [
        "[dis,uh,point]",
        "TSPNT"
    ],
    "disaster": [
        "[dih,zas,ter]",
        "TSSTR"
    ],
    "disc": [
        "[disk]",
        "TSK"
    ],
    "disciples": [
        "[dih,sahy,puhl,s]",
        "TSPLS"
    ],
    "disco": [
        "[dis,koh]",
        "TSK"
    ],
    "disconnect": [
        "[dis,kuh,nekt]",
        "TSKNKT"
    ],
    "discouraged": [
        "[dih,skur,ij,d]",
        "TSKRJT"
    ],
    "discover": [
        "[dih,skuhv,er]",
        "TSKFR"
    ],
    "discovered": [
        "['dih', 'skuhv', 'er', 'ed']",
        "TSKFRT"
    ],
    "discreet": [
        "[dih,skreet]",
        "TSKT"
    ],
    "discretion": [
        "['dih', 'skresh', 'uhn']",
        "TSKXN"
    ],
    "discriminate": [
        "['verbdih', 'skrim', 'uh', 'neyt']",
        "TSKMNT"
    ],
    "discuss": [
        "[dih,skuhs]",
        "TSKS"
    ],
    "discussing": [
        "[dih,skuhs,ing]",
        "TSKSNK"
    ],
    "discussion": [
        "['dih', 'skuhsh', 'uhn']",
        "TSKSN"
    ],
    "disease": [
        "['dih', 'zeez']",
        "TSS"
    ],
    "disgrace": [
        "[dis,greys]",
        "TSKRS"
    ],
    "disguise": [
        "['dis', 'gahyz']",
        "TSKS"
    ],
    "disguised": [
        "[dis,gahyz,d]",
        "TSKST"
    ],
    "disgust": [
        "['dis', 'guhst']",
        "TSKST"
    ],
    "disgusting": [
        "['dis', 'guhs', 'ting']",
        "TSKSTNK"
    ],
    "dish": [
        "[dish]",
        "TX"
    ],
    "dishes": [
        "['dish', 'es']",
        "TXS"
    ],
    "dishing": [
        "['dish', 'ing']",
        "TXNK"
    ],
    "dishonor": [
        "[dis,on,er]",
        "TXNR"
    ],
    "dismantle": [
        "['dis', 'man', 'tl']",
        "TSMNTL"
    ],
    "dismiss": [
        "['dis', 'mis']",
        "TSMS"
    ],
    "dismissed": [
        "['dis', 'mis', 'ed']",
        "TSMST"
    ],
    "disney": [
        "[diz,nee]",
        "TSN"
    ],
    "disown": [
        "[dis,ohn]",
        "TSN"
    ],
    "disowned": [
        "['dis', 'ohn', 'ed']",
        "TSNT"
    ],
    "display": [
        "[dih,spley]",
        "TSPL"
    ],
    "dispose": [
        "['dih', 'spohz']",
        "TSPS"
    ],
    "disregard": [
        "['dis', 'ri', 'gahrd']",
        "TSRKRT"
    ],
    "disrespect": [
        "['dis', 'ri', 'spekt']",
        "TSRSPKT"
    ],
    "disrespected": [
        "[dis,ri,spekt,ed]",
        "TSRSPKTT"
    ],
    "disrespectful": [
        "['dis', 'ri', 'spekt', 'fuhl']",
        "TSRSPKTFL"
    ],
    "disrespecting": [
        "['dis', 'ri', 'spekt', 'ing']",
        "TSRSPKTNK"
    ],
    "diss": [
        [
            "dee",
            "es"
        ],
        "TS"
    ],
    "dissect": [
        "['dih', 'sekt']",
        "TSKT"
    ],
    "dissed": [
        "['dis', 'sed']",
        "TST"
    ],
    "disses": [
        "[dis,ses]",
        "TSS"
    ],
    "dissing": [
        "['dis', 'sing']",
        "TSNK"
    ],
    "dissolve": [
        "[dih,zolv]",
        "TSLF"
    ],
    "distance": [
        "['dis', 'tuhns']",
        "TSTNS"
    ],
    "distant": [
        "['dis', 'tuhnt']",
        "TSTNT"
    ],
    "distorted": [
        "[dih,stawr,tid]",
        "TSTRTT"
    ],
    "distracted": [
        "['dih', 'strak', 'tid']",
        "TSTRKTT"
    ],
    "distractions": [
        "[dih,strak,shuhn,s]",
        "TSTRKXNS"
    ],
    "distress": [
        "[dih,stres]",
        "TSTRS"
    ],
    "distribute": [
        "[dih,strib,yoot]",
        "TSTRPT"
    ],
    "distribution": [
        "[dis,truh,byoo,shuhn]",
        "TSTRPXN"
    ],
    "district": [
        "['dis', 'trikt']",
        "TSTRKT"
    ],
    "disturb": [
        "['dih', 'sturb']",
        "TSTRP"
    ],
    "disturbed": [
        "[dih,sturbd]",
        "TSTRPT"
    ],
    "disturbing": [
        "[dih,stur,bing]",
        "TSTRPNK"
    ],
    "ditch": [
        "['dich']",
        "TX"
    ],
    "ditches": [
        "[dich,es]",
        "TXS"
    ],
    "diva": [
        "['dee', 'vuh']",
        "TF"
    ],
    "divas": [
        "['dee', 'vuh', 's']",
        "TFS"
    ],
    "dive": [
        "['dahyv']",
        "TF"
    ],
    "divide": [
        "['dih', 'vahyd']",
        "TFT"
    ],
    "divided": [
        "['dih', 'vahy', 'did']",
        "TFTT"
    ],
    "dividends": [
        "['div', 'i', 'dend', 's']",
        "TFTNTS"
    ],
    "divine": [
        "[dih,vahyn]",
        "TFN"
    ],
    "diving": [
        [
            "dahyv",
            "ing"
        ],
        "TFNK"
    ],
    "division": [
        "[dih,vizh,uhn]",
        "TFSN"
    ],
    "divorce": [
        "['dih', 'vawrs']",
        "TFRS"
    ],
    "divorced": [
        "['dih', 'vawrs', 'd']",
        "TFRST"
    ],
    "dixie": [
        "['dik', 'see']",
        "TKS"
    ],
    "dixon": [
        "['dik', 'suhn']",
        "TKSN"
    ],
    "dizzy": [
        "['diz', 'ee']",
        "TS"
    ],
    "dna": [
        "[(dn,)]",
        "TN"
    ],
    "do": [
        "['doo']",
        "T"
    ],
    "do's": [
        "[doo,'s]",
        "TS"
    ],
    "doc": [
        "['dok']",
        "TK"
    ],
    "dock": [
        "['dok']",
        "TK"
    ],
    "docked": [
        "[dok,ed]",
        "TKT"
    ],
    "doctor": [
        "['dok', 'ter']",
        "TKTR"
    ],
    "doctors": [
        "['dok', 'ter', 's']",
        "TKTRS"
    ],
    "dodge": [
        "[doj]",
        "TJ"
    ],
    "doe": [
        "['doh']",
        "T"
    ],
    "does": [
        "['dohz']",
        "TS"
    ],
    "doesn't": [
        "['duhz', 'uhnt']",
        "TSNNT"
    ],
    "dog": [
        "['dawg']",
        "TK"
    ],
    "doge": [
        "[dohj]",
        "TJ"
    ],
    "doggie": [
        [
            "dawg",
            "gee"
        ],
        "TJ"
    ],
    "dogging": [
        "[dawg,ging]",
        "TJNK"
    ],
    "doggy": [
        "[daw,gee]",
        "TK"
    ],
    "doghouse": [
        "[dog,hous]",
        "TS"
    ],
    "dogs": [
        "['dawg', 's']",
        "TKS"
    ],
    "doing": [
        "['doo', 'ing']",
        "TNK"
    ],
    "dolce": [
        "['dohl', 'chey']",
        "TLS"
    ],
    "doll": [
        "['dol']",
        "TL"
    ],
    "dollar": [
        "['dol', 'er']",
        "TLR"
    ],
    "dollars": [
        "['dol', 'er', 's']",
        "TLRS"
    ],
    "dolls": [
        "[dol,s]",
        "TLS"
    ],
    "dolly": [
        "['dol', 'ee']",
        "TL"
    ],
    "dolphin": [
        "['dol', 'fin']",
        "TLFN"
    ],
    "dolphins": [
        "['dol', 'fin', 's']",
        "TLFNS"
    ],
    "dom": [
        "['dom']",
        "TM"
    ],
    "domain": [
        "['doh', 'meyn']",
        "TMN"
    ],
    "dome": [
        "['dohm']",
        "TM"
    ],
    "domes": [
        "[dohm,s]",
        "TMS"
    ],
    "domestic": [
        "[duh,mes,tik]",
        "TMSTK"
    ],
    "dominate": [
        "['dom', 'uh', 'neyt']",
        "TMNT"
    ],
    "dominican": [
        "['duh', 'min', 'i', 'kuhn']",
        "TMNKN"
    ],
    "dominicans": [
        "[duh,min,i,kuhn,s]",
        "TMNKNS"
    ],
    "dominique": [
        "[dom,uh,neek]",
        "TMNK"
    ],
    "domino": [
        "['dom', 'uh', 'noh']",
        "TMN"
    ],
    "dominoes": [
        "['dom', 'uh', 'noh', 'es']",
        "TMNS"
    ],
    "don": [
        "['don']",
        "TN"
    ],
    "don's": [
        "[don,'s]",
        "TNNS"
    ],
    "don't": [
        "['dohnt']",
        "TNNT"
    ],
    "donald": [
        "['don', 'ld']",
        "TNLT"
    ],
    "done": [
        "['duhn']",
        "TN"
    ],
    "dong": [
        "[dawng]",
        "TNK"
    ],
    "donkey": [
        "['dong', 'kee']",
        "TNK"
    ],
    "donna": [
        "[dawn,nah]",
        "TN"
    ],
    "donor": [
        "['doh', 'ner']",
        "TNR"
    ],
    "dons": [
        "[don,s]",
        "TNS"
    ],
    "donut": [
        "['doh', 'nuht']",
        "TNT"
    ],
    "donuts": [
        "['doh', 'nuht', 's']",
        "TNTS"
    ],
    "doobie": [
        "['doo', 'bee']",
        "TP"
    ],
    "doodle": [
        "[dood,l]",
        "TTL"
    ],
    "doom": [
        "[doom]",
        "TM"
    ],
    "doomed": [
        "[doom,ed]",
        "TMT"
    ],
    "door": [
        "['dawr']",
        "TR"
    ],
    "door's": [
        "[dawr,'s]",
        "TRRS"
    ],
    "doorbell": [
        "['dawr', 'bel']",
        "TRPL"
    ],
    "doorman": [
        "[dawr,man]",
        "TRMN"
    ],
    "doormat": [
        "[dawr,mat]",
        "TRMT"
    ],
    "doors": [
        "['dawr', 's']",
        "TRS"
    ],
    "doorstep": [
        "[dawr,step]",
        "TRSTP"
    ],
    "doorway": [
        "[dawr,wey]",
        "TR"
    ],
    "dope": [
        "['dohp']",
        "TP"
    ],
    "dopeboy": [
        [
            "dohp",
            "boi"
        ],
        "TPP"
    ],
    "doped": [
        "['dohp', 'd']",
        "TPT"
    ],
    "dora": [
        "['dawr', 'uh']",
        "TR"
    ],
    "dork": [
        "[dawrk]",
        "TRK"
    ],
    "dorks": [
        "['dawrk', 's']",
        "TRKS"
    ],
    "dos": [
        "['daws']",
        "TS"
    ],
    "dosage": [
        "['doh', 'sij']",
        "TSJ"
    ],
    "dose": [
        "['dohs']",
        "TS"
    ],
    "dot": [
        "['dot']",
        "TT"
    ],
    "dots": [
        "['dot', 's']",
        "TTS"
    ],
    "dotted": [
        "[dot,id]",
        "TTT"
    ],
    "double": [
        "['duhb', 'uhl']",
        "TPL"
    ],
    "doubled": [
        "['duhb', 'uhl', 'd']",
        "TPLT"
    ],
    "doubles": [
        "[duhb,uhl,s]",
        "TPLS"
    ],
    "doubling": [
        "[duhb,ling]",
        "TPLNK"
    ],
    "doubt": [
        "['dout']",
        "TPT"
    ],
    "doubted": [
        "['dout', 'ed']",
        "TPTT"
    ],
    "doubting": [
        "[dout,ing]",
        "TPTNK"
    ],
    "doubts": [
        "[dout,s]",
        "TPTS"
    ],
    "dough": [
        "['doh']",
        "T"
    ],
    "doughboy": [
        "[doh,boi]",
        "TP"
    ],
    "doughnut": [
        "[doh,nuht]",
        "TNT"
    ],
    "doughnuts": [
        "[doh,nuht,s]",
        "TNTS"
    ],
    "doughs": [
        "[doh,s]",
        "TS"
    ],
    "dove": [
        "[duhv]",
        "TF"
    ],
    "doves": [
        "['duhv', 's']",
        "TFS"
    ],
    "down": [
        "['doun']",
        "TN"
    ],
    "downers": [
        "[dou,ner,s]",
        "TNRS"
    ],
    "downfall": [
        "['doun', 'fawl']",
        "TNFL"
    ],
    "downgraded": [
        "['doun', 'greyd', 'd']",
        "TNKRTT"
    ],
    "downing": [
        "[dou,ning]",
        "TNNK"
    ],
    "download": [
        "[doun,lohd]",
        "TNLT"
    ],
    "downs": [
        "['doun', 's']",
        "TNS"
    ],
    "downstairs": [
        "[adverb]",
        "TNSTRS"
    ],
    "downtime": [
        "[doun,tahym]",
        "TNTM"
    ],
    "downtown": [
        "['doun', 'toun']",
        "TNTN"
    ],
    "doze": [
        "[dohz]",
        "TS"
    ],
    "dozen": [
        "['duhz', 'uhn']",
        "TSN"
    ],
    "dozens": [
        "[duhz,uhn,s]",
        "TSNS"
    ],
    "draco": [
        "['drey', 'koh']",
        "TRK"
    ],
    "dracos": [
        "['drey', 'koh', 's']",
        "TRKS"
    ],
    "dracula": [
        "['drak', 'yuh', 'luh']",
        "TRKL"
    ],
    "draft": [
        "[draft]",
        "TRFT"
    ],
    "drafted": [
        "[draft,ed]",
        "TRFTT"
    ],
    "drag": [
        "['drag']",
        "TRK"
    ],
    "dragged": [
        "['drag', 'ged']",
        "TRKT"
    ],
    "dragging": [
        "['drag', 'ing']",
        "TRJNK"
    ],
    "dragon": [
        "['drag', 'uhn']",
        "TRKN"
    ],
    "dragons": [
        "['drag', 'uhn', 's']",
        "TRKNS"
    ],
    "drain": [
        "['dreyn']",
        "TRN"
    ],
    "drake": [
        "['dreyk']",
        "TRK"
    ],
    "drake's": [
        "[dreyk,'s]",
        "TRKS"
    ],
    "drama": [
        "['drah', 'muh']",
        "TRM"
    ],
    "dramatic": [
        "[druh,mat,ik]",
        "TRMTK"
    ],
    "drank": [
        "['drangk']",
        "TRNK"
    ],
    "drape": [
        "[dreyp]",
        "TRP"
    ],
    "draped": [
        "['dreyp', 'd']",
        "TRPT"
    ],
    "drapes": [
        "[dreyp,s]",
        "TRPS"
    ],
    "drastic": [
        "['dras', 'tik']",
        "TRSTK"
    ],
    "draw": [
        "['draw']",
        "TR"
    ],
    "drawer": [
        "['drawrfor1']",
        "TRR"
    ],
    "drawers": [
        "['drawrfor1', 's']",
        "TRRS"
    ],
    "drawing": [
        "['draw', 'ing']",
        "TRNK"
    ],
    "drawl": [
        "[drawl]",
        "TRL"
    ],
    "drawls": [
        "['drawl', 's']",
        "TRLS"
    ],
    "drawn": [
        "['drawn']",
        "TRN"
    ],
    "draws": [
        "['draw', 's']",
        "TRS"
    ],
    "dread": [
        "['dred']",
        "TRT"
    ],
    "dreaded": [
        "['dred', 'ed']",
        "TRTT"
    ],
    "dreadlocks": [
        "['dred', 'loks']",
        "TRTLKS"
    ],
    "dreads": [
        "['dred', 's']",
        "TRTS"
    ],
    "dream": [
        "['dreem']",
        "TRM"
    ],
    "dreamed": [
        "['dreem', 'ed']",
        "TRMT"
    ],
    "dreamer": [
        "[dree,mer]",
        "TRMR"
    ],
    "dreaming": [
        "['dreem', 'ing']",
        "TRMNK"
    ],
    "dreams": [
        "['dreem', 's']",
        "TRMS"
    ],
    "dreamt": [
        "[dremt]",
        "TRMT"
    ],
    "dreamy": [
        "[dree,mee]",
        "TRM"
    ],
    "drench": [
        "[drench]",
        "TRNX"
    ],
    "dress": [
        "['dres']",
        "TRS"
    ],
    "dressed": [
        "['dres', 'ed']",
        "TRST"
    ],
    "dresser": [
        "['dres', 'er']",
        "TRSR"
    ],
    "dresses": [
        "[dres,es]",
        "TRSS"
    ],
    "dressing": [
        "['dres', 'ing']",
        "TRSNK"
    ],
    "drew": [
        "[droo]",
        "TR"
    ],
    "dribble": [
        "['drib', 'uhl']",
        "TRPL"
    ],
    "dried": [
        "[drahyd]",
        "TRT"
    ],
    "dries": [
        "[drahyz]",
        "TRS"
    ],
    "drift": [
        "['drift']",
        "TRFT"
    ],
    "drifting": [
        "['drift', 'ing']",
        "TRFTNK"
    ],
    "drill": [
        "['dril']",
        "TRL"
    ],
    "drilling": [
        "['dril', 'ing']",
        "TRLNK"
    ],
    "drills": [
        "[dril,s]",
        "TRLS"
    ],
    "drink": [
        "['dringk']",
        "TRNK"
    ],
    "drinker": [
        "['dring', 'ker']",
        "TRNKR"
    ],
    "drinkers": [
        "[dring,ker,s]",
        "TRNKRS"
    ],
    "drinking": [
        "['dring', 'king']",
        "TRNKNK"
    ],
    "drinks": [
        "['dringk', 's']",
        "TRNKS"
    ],
    "drip": [
        "['drip']",
        "TRP"
    ],
    "dripped": [
        "[drip,ped]",
        "TRPT"
    ],
    "dripping": [
        "['drip', 'ing']",
        "TRPNK"
    ],
    "drive": [
        "['drahyv']",
        "TRF"
    ],
    "driven": [
        "['driv', 'uhn']",
        "TRFN"
    ],
    "driver": [
        "['drahy', 'ver']",
        "TRFR"
    ],
    "driver's": [
        "['drahy', 'ver', \"'s\"]",
        "TRFRRS"
    ],
    "drivers": [
        "[drahy,ver,s]",
        "TRFRS"
    ],
    "drives": [
        "['drahyv', 's']",
        "TRFS"
    ],
    "driveway": [
        "['drahyv', 'wey']",
        "TRF"
    ],
    "driveways": [
        "[drahyv,wey,s]",
        "TRFS"
    ],
    "driving": [
        "['drahy', 'ving']",
        "TRFNK"
    ],
    "drizzle": [
        "[driz,uhl]",
        "TRSL"
    ],
    "drones": [
        "['drohn', 's']",
        "TRNS"
    ],
    "drool": [
        "['drool']",
        "TRL"
    ],
    "drooling": [
        "['drool', 'ing']",
        "TRLNK"
    ],
    "drop": [
        "['drop']",
        "TRP"
    ],
    "dropout": [
        "[drop,out]",
        "TRPT"
    ],
    "dropped": [
        "['drop', 'ped']",
        "TRPT"
    ],
    "dropping": [
        "['drop', 'ing']",
        "TRPNK"
    ],
    "drops": [
        "['drop', 's']",
        "TRPS"
    ],
    "drought": [
        "['drout']",
        "TRFT"
    ],
    "droughts": [
        "[drout,s]",
        "TRFTS"
    ],
    "drove": [
        "['drohv']",
        "TRF"
    ],
    "drown": [
        "['droun']",
        "TRN"
    ],
    "drowned": [
        "['droun', 'ed']",
        "TRNT"
    ],
    "drowning": [
        "['droun', 'ing']",
        "TRNNK"
    ],
    "drowsy": [
        "[drou,zee]",
        "TRS"
    ],
    "drug": [
        "['druhg']",
        "TRK"
    ],
    "drugged": [
        "[druhg,ged]",
        "TRKT"
    ],
    "drugs": [
        "['druhg', 's']",
        "TRKS"
    ],
    "drum": [
        "['druhm']",
        "TRM"
    ],
    "drummer": [
        "['druhm', 'er']",
        "TRMR"
    ],
    "drumming": [
        "[druhm,ming]",
        "TRMNK"
    ],
    "drums": [
        "['druhm', 's']",
        "TRMS"
    ],
    "drunk": [
        "['druhngk']",
        "TRNK"
    ],
    "dry": [
        "['drahy']",
        "TR"
    ],
    "dryer": [
        "['drahy', 'er']",
        "TRR"
    ],
    "drying": [
        "['drahy', 'ing']",
        "TRNK"
    ],
    "ds": [
        "[dee]",
        "TS"
    ],
    "dual": [
        "[doo,uhl]",
        "TL"
    ],
    "dub": [
        "['duhb']",
        "TP"
    ],
    "dubai": [
        "['doo', 'bahy']",
        "TP"
    ],
    "dubbed": [
        "[duhb,bed]",
        "TPT"
    ],
    "dublin": [
        "[duhb,lin]",
        "TPLN"
    ],
    "dubs": [
        "['duhb', 's']",
        "TPS"
    ],
    "duce": [
        "['doo', 'chey']",
        "TS"
    ],
    "duck": [
        "['duhk']",
        "TK"
    ],
    "ducked": [
        "['duhk', 'ed']",
        "TKT"
    ],
    "ducking": [
        "['duhk', 'ing']",
        "TKNK"
    ],
    "ducks": [
        "['duhk', 's']",
        "TKS"
    ],
    "duct": [
        "['duhkt']",
        "TKT"
    ],
    "dud": [
        "['duhd']",
        "TT"
    ],
    "dude": [
        "['dood']",
        "TT"
    ],
    "dude's": [
        "[dood,'s]",
        "TTS"
    ],
    "dudes": [
        "['dood', 's']",
        "TTS"
    ],
    "due": [
        "['doo']",
        "T"
    ],
    "dues": [
        "['doo', 's']",
        "TS"
    ],
    "duet": [
        "[doo,et]",
        "TT"
    ],
    "duff": [
        "[duhf]",
        "TF"
    ],
    "duffel": [
        "[duhf,uhl]",
        "TFL"
    ],
    "dug": [
        "['duhg']",
        "TK"
    ],
    "duke": [
        "['dook']",
        "TK"
    ],
    "dukes": [
        "['dook', 's']",
        "TKS"
    ],
    "dumb": [
        "['duhm']",
        "TMP"
    ],
    "dumber": [
        "['duhm', 'er']",
        "TMPR"
    ],
    "dumbest": [
        "[duhm,est]",
        "TMPST"
    ],
    "dummy": [
        "['duhm', 'ee']",
        "TM"
    ],
    "dump": [
        "['duhmp']",
        "TMP"
    ],
    "dumped": [
        "['duhmp', 'ed']",
        "TMPT"
    ],
    "dumping": [
        "[duhmp,ing]",
        "TMPNK"
    ],
    "dun": [
        "['duhn']",
        "TN"
    ],
    "duncan": [
        "[duhng,kuhn]",
        "TNKN"
    ],
    "dundee": [
        "['duhn', 'dee']",
        "TNT"
    ],
    "dungarees": [
        "['duhng', 'guh', 'ree', 's']",
        "TNKRS"
    ],
    "dungeon": [
        "['duhn', 'juhn']",
        "TNJN"
    ],
    "dungeons": [
        "[duhn,juhn,s]",
        "TNJNS"
    ],
    "dunk": [
        "['duhngk']",
        "TNK"
    ],
    "dunking": [
        "['duhng', 'king']",
        "TNKNK"
    ],
    "dunno": [
        "['duh', 'noh']",
        "TN"
    ],
    "duo": [
        "[doo,oh]",
        "T"
    ],
    "duplex": [
        "[doo,pleks]",
        "TPLKS"
    ],
    "duplicate": [
        "[noun]",
        "TPLKT"
    ],
    "dura": [
        "[door,uh]",
        "TR"
    ],
    "durant": [
        "['duh', 'rant']",
        "TRNT"
    ],
    "during": [
        "['door', 'ing']",
        "TRNK"
    ],
    "dusk": [
        "[duhsk]",
        "TSK"
    ],
    "dust": [
        "['duhst']",
        "TST"
    ],
    "dusted": [
        "[duhst,ed]",
        "TSTT"
    ],
    "dusting": [
        "['duhs', 'ting']",
        "TSTNK"
    ],
    "dusty": [
        "['duhs', 'tee']",
        "TST"
    ],
    "dutch": [
        "['duhch']",
        "TX"
    ],
    "duty": [
        "['doo', 'tee']",
        "TT"
    ],
    "dvd": [
        "[dv,d]",
        "TFT"
    ],
    "dwell": [
        "[dwel]",
        "TL"
    ],
    "dweller": [
        "['dwel', 'er']",
        "TLR"
    ],
    "dwelling": [
        "[dwel,ing]",
        "TLNK"
    ],
    "dy": [
        "[ds,prz,m]",
        "T"
    ],
    "dye": [
        "['dahy']",
        "T"
    ],
    "dyed": [
        "['dahy', 'd']",
        "TT"
    ],
    "dying": [
        "['dahy', 'ing']",
        "TNK"
    ],
    "dyke": [
        "['dahyk']",
        "TK"
    ],
    "dykes": [
        "['dahyk', 's']",
        "TKS"
    ],
    "dynamite": [
        "[dahy,nuh,mahyt]",
        "TNMT"
    ],
    "dynasty": [
        "['dahy', 'nuh', 'stee']",
        "TNST"
    ],
    "e": [
        "['ee', '']",
        "A"
    ],
    "ea": [
        "['ey', 'ah']",
        "A"
    ],
    "each": [
        "['eech']",
        "AX"
    ],
    "eager": [
        "[ee,ger]",
        "AKR"
    ],
    "eagle": [
        "['ee', 'guhl']",
        "AKL"
    ],
    "eagles": [
        "[ee,guhl,s]",
        "AKLS"
    ],
    "ear": [
        "['eer']",
        "AR"
    ],
    "earl": [
        "['url']",
        "ARL"
    ],
    "earlobe": [
        "[eer,lohb]",
        "ARLP"
    ],
    "early": [
        "['ur', 'lee']",
        "ARL"
    ],
    "earn": [
        "['urn']",
        "ARN"
    ],
    "earned": [
        "['urn', 'ed']",
        "ARNT"
    ],
    "earning": [
        "['urn', 'ing']",
        "ARNNK"
    ],
    "earring": [
        "['eer', 'ring']",
        "ARNK"
    ],
    "earrings": [
        "['eer', 'ring', 's']",
        "ARNKS"
    ],
    "ears": [
        "['eer', 's']",
        "ARS"
    ],
    "earth": [
        "['urth']",
        "AR0"
    ],
    "earth's": [
        "[urth,'s]",
        "AR00"
    ],
    "earthquake": [
        "['urth', 'kweyk']",
        "AR0KK"
    ],
    "ease": [
        "['eez']",
        "AS"
    ],
    "easier": [
        "['ee', 'zee', 'er']",
        "AS"
    ],
    "easily": [
        "['ee', 'zuh', 'lee']",
        "ASL"
    ],
    "east": [
        "['eest']",
        "AST"
    ],
    "easter": [
        "['ee', 'ster']",
        "ASTR"
    ],
    "easy": [
        "['ee', 'zee']",
        "AS"
    ],
    "eat": [
        "['eet']",
        "AT"
    ],
    "eater": [
        "['eet', 'er']",
        "ATR"
    ],
    "eating": [
        "['ee', 'ting']",
        "ATNK"
    ],
    "eats": [
        "['eet', 's']",
        "ATS"
    ],
    "eavesdropping": [
        "['eevz', 'drop', 'ping']",
        "AFSTRPNK"
    ],
    "ebonics": [
        "[ih,bon,iks]",
        "APNKS"
    ],
    "ebony": [
        "[eb,uh,nee]",
        "APN"
    ],
    "echelon": [
        "['esh', 'uh', 'lon']",
        "AXLN"
    ],
    "echo": [
        "['ek', 'oh']",
        "AX"
    ],
    "eclipse": [
        "[ih,klips]",
        "AKLPS"
    ],
    "economical": [
        "[ek,uh,nom,i,kuhl]",
        "AKNMKL"
    ],
    "economy": [
        "['ih', 'kon', 'uh', 'mee']",
        "AKNM"
    ],
    "ecstacy": [
        [
            "ek",
            "stuh",
            "see"
        ],
        "AKSTS"
    ],
    "ecstasy": [
        "['ek', 'stuh', 'see']",
        "AKSTS"
    ],
    "ed": [
        "['ed']",
        "AT"
    ],
    "eddy": [
        "['ed', 'ee']",
        "AT"
    ],
    "edge": [
        "['ej']",
        "AJ"
    ],
    "edges": [
        "[ej,s]",
        "AJS"
    ],
    "edible": [
        "['ed', 'uh', 'buhl']",
        "ATPL"
    ],
    "edison": [
        "[ed,uh,suhn]",
        "ATSN"
    ],
    "edit": [
        "[ed,it]",
        "ATT"
    ],
    "edition": [
        "['ih', 'dish', 'uhn']",
        "ATXN"
    ],
    "educated": [
        "[ej,oo,key,tid]",
        "ATKTT"
    ],
    "education": [
        "[ej,oo,key,shuhn]",
        "ATKXN"
    ],
    "effect": [
        "['ih', 'fekt']",
        "AFKT"
    ],
    "effects": [
        "['ih', 'fekts']",
        "AFKTS"
    ],
    "effed": [
        "[ef,ed]",
        "AFT"
    ],
    "effing": [
        "['ef', 'ing']",
        "AFNK"
    ],
    "effort": [
        "['ef', 'ert']",
        "AFRT"
    ],
    "effortless": [
        "[ef,ert,lis]",
        "AFRTLS"
    ],
    "egg": [
        "['eg']",
        "AK"
    ],
    "eggbeater": [
        "[eg,bee,ter]",
        "AKPTR"
    ],
    "eggs": [
        "['eg', 's']",
        "AKS"
    ],
    "ego": [
        "['ee', 'goh']",
        "AK"
    ],
    "egypt": [
        "[ee,jipt]",
        "AJPT"
    ],
    "egyptian": [
        "['ih', 'jip', 'shuhn']",
        "AJPXN"
    ],
    "egyptians": [
        "[ih,jip,shuhn,s]",
        "AJPXNS"
    ],
    "eh": [
        "['ey']",
        "A"
    ],
    "eiffel": [
        "['ahy', 'fuhl']",
        "AFL"
    ],
    "eight": [
        "['eyt']",
        "AT"
    ],
    "eighteen": [
        "[ey,teen]",
        "ATN"
    ],
    "eighth": [
        "['eytth']",
        "A0"
    ],
    "eights": [
        "[eyts]",
        "ATS"
    ],
    "eighty": [
        "['ey', 'tee']",
        "AT"
    ],
    "einstein": [
        "['ahyn', 'stahyn']",
        "ANSTN"
    ],
    "either": [
        "['ee', 'ther']",
        "A0R"
    ],
    "ejected": [
        "[ih,jekt,ed]",
        "AJKTT"
    ],
    "el": [
        "['el']",
        "AL"
    ],
    "elaborate": [
        "['adjectiveih', 'lab', 'er', 'it']",
        "ALPRT"
    ],
    "elastic": [
        "['ih', 'las', 'tik']",
        "ALSTK"
    ],
    "elated": [
        "['ih', 'ley', 'tid']",
        "ALTT"
    ],
    "elbow": [
        "['el', 'boh']",
        "ALP"
    ],
    "elbows": [
        "[el,boh,s]",
        "ALPS"
    ],
    "elders": [
        "['el', 'der', 's']",
        "ALTRS"
    ],
    "elected": [
        "[ih,lek,tid]",
        "ALKTT"
    ],
    "election": [
        "['ih', 'lek', 'shuhn']",
        "ALKXN"
    ],
    "electric": [
        "['ih', 'lek', 'trik']",
        "ALKTRK"
    ],
    "elegant": [
        "['el', 'i', 'guhnt']",
        "ALKNT"
    ],
    "element": [
        "[el,uh,muhnt]",
        "ALMNT"
    ],
    "elementary": [
        "[el,uh,men,tuh,ree]",
        "ALMNTR"
    ],
    "elements": [
        "['el', 'uh', 'muhnt', 's']",
        "ALMNTS"
    ],
    "elephant": [
        "['el', 'uh', 'fuhnt']",
        "ALFNT"
    ],
    "elephants": [
        "['el', 'uh', 'fuhnt', 's']",
        "ALFNTS"
    ],
    "elevate": [
        "['verbel', 'uh', 'veyt']",
        "ALFT"
    ],
    "elevator": [
        "['el', 'uh', 'vey', 'ter']",
        "ALFTR"
    ],
    "elevators": [
        "[el,uh,vey,ter,s]",
        "ALFTRS"
    ],
    "eleven": [
        "['ih', 'lev', 'uhn']",
        "ALFN"
    ],
    "elite": [
        "[ih,leet]",
        "ALT"
    ],
    "ella": [
        "['el', 'uh']",
        "AL"
    ],
    "ellis": [
        "['el', 'is']",
        "ALS"
    ],
    "elm": [
        "['elm']",
        "ALM"
    ],
    "else": [
        "['els']",
        "ALS"
    ],
    "elvis": [
        "['el', 'vis']",
        "ALFS"
    ],
    "em": [
        "['em']",
        "AM"
    ],
    "email": [
        "['ee', 'meyl']",
        "AML"
    ],
    "embalming": [
        "['em', 'bahm', 'ing']",
        "AMPLMNK"
    ],
    "embarrass": [
        "['em', 'bar', 'uhs']",
        "AMPRS"
    ],
    "embarrassed": [
        "['em', 'bar', 'uhs', 'ed']",
        "AMPRST"
    ],
    "embarrassing": [
        "['em', 'bar', 'uhs', 'ing']",
        "AMPRSNK"
    ],
    "embassy": [
        "['em', 'buh', 'see']",
        "AMPS"
    ],
    "embody": [
        "[em,bod,ee]",
        "AMPT"
    ],
    "embrace": [
        "[em,breys]",
        "AMPRS"
    ],
    "embryo": [
        "[em,bree,oh]",
        "AMPR"
    ],
    "emcee": [
        "[em,see]",
        "AMS"
    ],
    "emcee's": [
        "[em,see,'s]",
        "AMSS"
    ],
    "emcees": [
        "[em,see,s]",
        "AMSS"
    ],
    "emerge": [
        "[ih,murj]",
        "AMRJ"
    ],
    "emergency": [
        "['ih', 'mur', 'juhn', 'see']",
        "AMRJNS"
    ],
    "emmy": [
        "['em', 'ee']",
        "AM"
    ],
    "emoji": [
        "['ih', 'moh', 'jee']",
        "AMJ"
    ],
    "emotion": [
        "['ih', 'moh', 'shuhn']",
        "AMXN"
    ],
    "emotional": [
        "['ih', 'moh', 'shuh', 'nl']",
        "AMXNL"
    ],
    "emotionally": [
        "[ih,moh,shuh,nl,ly]",
        "AMXNL"
    ],
    "emotions": [
        "['ih', 'moh', 'shuhn', 's']",
        "AMXNS"
    ],
    "empathy": [
        "['em', 'puh', 'thee']",
        "AMP0"
    ],
    "emphasis": [
        "['em', 'fuh', 'sis']",
        "AMFSS"
    ],
    "empire": [
        "['em', 'pahyuhr']",
        "AMPR"
    ],
    "employ": [
        "['em', 'ploi']",
        "AMPL"
    ],
    "employees": [
        "[em,ploi,ee,s]",
        "AMPLS"
    ],
    "empty": [
        "['emp', 'tee']",
        "AMPT"
    ],
    "emptying": [
        "[emp,tee,ing]",
        "AMPTNK"
    ],
    "ems": [
        "['em']",
        "AMS"
    ],
    "en": [
        "['en']",
        "AN"
    ],
    "enchilada": [
        "[en,chuh,lah,duh]",
        "ANXLT"
    ],
    "encore": [
        "['ahng', 'kawr']",
        "ANKR"
    ],
    "encourage": [
        "['en', 'kur', 'ij']",
        "ANKRJ"
    ],
    "end": [
        "['end']",
        "ANT"
    ],
    "ended": [
        "['end', 'ed']",
        "ANTT"
    ],
    "ending": [
        "['en', 'ding']",
        "ANTNK"
    ],
    "endings": [
        "[en,ding,s]",
        "ANTNKS"
    ],
    "endless": [
        "[end,lis]",
        "ANTLS"
    ],
    "endlessly": [
        "[end,lis,ly]",
        "ANTLSL"
    ],
    "endorsements": [
        "[en,dawrs,muhntorin,dawrs,muhnt,s]",
        "ANTRSMNTS"
    ],
    "ends": [
        "['end', 's']",
        "ANTS"
    ],
    "endurance": [
        "[en,door,uhns]",
        "ANTRNS"
    ],
    "endure": [
        "[en,door]",
        "ANTR"
    ],
    "enemy": [
        "['en', 'uh', 'mee']",
        "ANM"
    ],
    "enemy's": [
        "[en,uh,mee,'s]",
        "ANMS"
    ],
    "energizer": [
        "[en,er,jahy,zer]",
        "ANRJSR"
    ],
    "energy": [
        "['en', 'er', 'jee']",
        "ANRJ"
    ],
    "enforcement": [
        "[en,fawrs,muhnt]",
        "ANFRSMNT"
    ],
    "engaged": [
        "[en,geyjd]",
        "ANKJT"
    ],
    "engagement": [
        "['en', 'geyj', 'muhnt']",
        "ANKJMNT"
    ],
    "engine": [
        "['en', 'juhn']",
        "ANJN"
    ],
    "engineer": [
        "[en,juh,neer]",
        "ANJNR"
    ],
    "engines": [
        "[en,juhn,s]",
        "ANJNS"
    ],
    "england": [
        "[ing,gluhndor]",
        "ANKLNT"
    ],
    "english": [
        "['ing', 'glishor']",
        "ANKLX"
    ],
    "engulfed": [
        "[en,guhlf,ed]",
        "ANKLFT"
    ],
    "enhance": [
        "[en,hans]",
        "ANNS"
    ],
    "enjoy": [
        "['en', 'joi']",
        "ANJ"
    ],
    "enjoyed": [
        "[en,joi,ed]",
        "ANJT"
    ],
    "enjoying": [
        "[en,joi,ing]",
        "ANJNK"
    ],
    "enlighten": [
        "[en,lahyt,n]",
        "ANLTN"
    ],
    "enormous": [
        "['ih', 'nawr', 'muhs']",
        "ANRMS"
    ],
    "enough": [
        "['ih', 'nuhf']",
        "ANK"
    ],
    "enter": [
        "['en', 'ter']",
        "ANTR"
    ],
    "entered": [
        "[en,ter,ed]",
        "ANTRT"
    ],
    "entering": [
        "[en,ter,ing]",
        "ANTRNK"
    ],
    "entertain": [
        "['en', 'ter', 'teyn']",
        "ANTRTN"
    ],
    "entertained": [
        "['en', 'ter', 'teyn', 'ed']",
        "ANTRTNT"
    ],
    "entertainer": [
        "[en,ter,tey,ner]",
        "ANTRTNR"
    ],
    "entertaining": [
        "[en,ter,tey,ning]",
        "ANTRTNNK"
    ],
    "entertainment": [
        "['en', 'ter', 'teyn', 'muhnt']",
        "ANTRTNMNT"
    ],
    "entice": [
        "[en,tahys]",
        "ANTS"
    ],
    "entire": [
        "['en', 'tahyuhr']",
        "ANTR"
    ],
    "entirely": [
        "[en,tahyuhr,lee]",
        "ANTRL"
    ],
    "entitled": [
        "['en', 'tahyt', 'l', 'd']",
        "ANTTLT"
    ],
    "entourage": [
        "[ahn,too,rahzh]",
        "ANTRJ"
    ],
    "entrance": [
        "['en', 'truhns']",
        "ANTRNS"
    ],
    "entrepreneur": [
        "['ahn', 'truh', 'pruh', 'nur']",
        "ANTRPRNR"
    ],
    "entry": [
        "[en,tree]",
        "ANTR"
    ],
    "envelope": [
        "[en,vuh,lohp]",
        "ANFLP"
    ],
    "envelopes": [
        "[en,vuh,lohp,s]",
        "ANFLPS"
    ],
    "envious": [
        "[en,vee,uhs]",
        "ANFS"
    ],
    "environment": [
        "['en', 'vahy', 'ruhn', 'muhnt']",
        "ANFRNMNT"
    ],
    "envision": [
        "[en,vizh,uhn]",
        "ANFSN"
    ],
    "envy": [
        "['en', 'vee']",
        "ANF"
    ],
    "epic": [
        "['ep', 'ik']",
        "APK"
    ],
    "epiphany": [
        "[ih,pif,uh,nee]",
        "APFN"
    ],
    "episode": [
        "['ep', 'uh', 'sohd']",
        "APST"
    ],
    "epitome": [
        "['ih', 'pit', 'uh', 'mee']",
        "APTM"
    ],
    "equal": [
        "['ee', 'kwuhl']",
        "AKL"
    ],
    "equality": [
        "[ih,kwol,i,tee]",
        "AKLT"
    ],
    "equals": [
        "[ee,kwuhl,s]",
        "AKLS"
    ],
    "equipped": [
        "['ih', 'kwip', 'ped']",
        "AKPT"
    ],
    "equity": [
        "[ek,wi,tee]",
        "AKT"
    ],
    "equivalent": [
        "[ih,kwiv,uh,luhntorfor5]",
        "AKFLNT"
    ],
    "er": [
        "['uh']",
        "AR"
    ],
    "era": [
        "[eer,uh]",
        "AR"
    ],
    "erase": [
        "['ih', 'reys']",
        "ARS"
    ],
    "erased": [
        "[ih,reys,d]",
        "ARST"
    ],
    "eraser": [
        "[ih,rey,ser]",
        "ARSR"
    ],
    "erect": [
        "[ih,rekt]",
        "ARKT"
    ],
    "erection": [
        "[ih,rek,shuhn]",
        "ARKXN"
    ],
    "erg": [
        "[urg]",
        "ARK"
    ],
    "erica": [
        "[er,i,kuh]",
        "ARK"
    ],
    "erotic": [
        "[ih,rot,ik]",
        "ARTK"
    ],
    "err": [
        "['ur']",
        "AR"
    ],
    "error": [
        "[er,er]",
        "ARR"
    ],
    "erupt": [
        "[ih,ruhpt]",
        "ARPT"
    ],
    "erving": [
        "['ur', 'ving']",
        "ARFNK"
    ],
    "es": [
        "[ee]",
        "AS"
    ],
    "escalade": [
        "['es', 'kuh', 'leyd']",
        "ASKLT"
    ],
    "escalades": [
        "[es,kuh,leyd,s]",
        "ASKLTS"
    ],
    "escalator": [
        "['es', 'kuh', 'ley', 'ter']",
        "ASKLTR"
    ],
    "escape": [
        "['ih', 'skeyp']",
        "ASKP"
    ],
    "escaped": [
        "[ih,skeyp,d]",
        "ASKPT"
    ],
    "ese": [
        [
            "ee",
            "es",
            "ee"
        ],
        "AS"
    ],
    "eses": [
        [
            "ez",
            "eez"
        ],
        "ASS"
    ],
    "eskimo": [
        "['es', 'kuh', 'moh']",
        "ASKM"
    ],
    "esophagus": [
        "[ih,sof,uh,guhs]",
        "ASFKS"
    ],
    "esoteric": [
        "[es,uh,ter,ik]",
        "ASTRK"
    ],
    "especially": [
        "['ih', 'spesh', 'uh', 'lee']",
        "ASPSL"
    ],
    "espy": [
        "['ih', 'spahy']",
        "ASP"
    ],
    "essence": [
        "['es', 'uhns']",
        "ASNS"
    ],
    "est": [
        "[lah,boh,rah,reestoh,rah,re]",
        "AST"
    ],
    "established": [
        "[ih,stab,lish,ed]",
        "ASTPLXT"
    ],
    "establishing": [
        "['ih', 'stab', 'lish', 'ing']",
        "ASTPLXNK"
    ],
    "estate": [
        "['ih', 'steyt']",
        "ASTT"
    ],
    "estates": [
        "[ih,steyt,s]",
        "ASTTS"
    ],
    "esteem": [
        "['ih', 'steem']",
        "ASTM"
    ],
    "esther": [
        "['es', 'ter']",
        "AS0R"
    ],
    "estranged": [
        "[ih,streynjd]",
        "ASTRNJT"
    ],
    "estrogen": [
        "['es', 'truh', 'juhn']",
        "ASTRJN"
    ],
    "etcetera": [
        "[et,set,er,uh]",
        "ATSTR"
    ],
    "eternal": [
        "[ih,tur,nl]",
        "ATRNL"
    ],
    "eternity": [
        "['ih', 'tur', 'ni', 'tee']",
        "ATRNT"
    ],
    "ether": [
        "['ee', 'ther']",
        "A0R"
    ],
    "ethiopian": [
        "[ee,thee,oh,pee,uhn]",
        "A0PN"
    ],
    "etiquette": [
        "['et', 'i', 'kit']",
        "ATKT"
    ],
    "euphoria": [
        "['yoo', 'fawr', 'ee', 'uh']",
        "AFR"
    ],
    "euro": [
        "['yoor', 'oh']",
        "AR"
    ],
    "europe": [
        "['yoor', 'uhp']",
        "ARP"
    ],
    "european": [
        "['yoor', 'uh', 'pee', 'uhn']",
        "ARPN"
    ],
    "euros": [
        "['yoor', 'oh', 's']",
        "ARS"
    ],
    "evasive": [
        "[ih,vey,siv]",
        "AFSF"
    ],
    "eve": [
        "['eev']",
        "AF"
    ],
    "even": [
        "['ee', 'vuhn']",
        "AFN"
    ],
    "evening": [
        "['eev', 'ning']",
        "AFNNK"
    ],
    "evenings": [
        "[eev,ningz]",
        "AFNNKS"
    ],
    "event": [
        "[ih,vent]",
        "AFNT"
    ],
    "events": [
        "[ih,vent,s]",
        "AFNTS"
    ],
    "eventually": [
        "[ih,ven,choo,uh,lee]",
        "AFNTL"
    ],
    "ever": [
        "['ev', 'er']",
        "AFR"
    ],
    "everest": [
        "[ev,er,ist]",
        "AFRST"
    ],
    "everlasting": [
        "['ev', 'er', 'las', 'ting']",
        "AFRLSTNK"
    ],
    "every": [
        "['ev', 'ree']",
        "AFR"
    ],
    "everybody": [
        "['ev', 'ree', 'bod', 'ee']",
        "AFRPT"
    ],
    "everyday": [
        "['adjectiveev', 'ree', 'dey']",
        "AFRT"
    ],
    "everynight": [
        [
            "ev",
            "ree",
            "nahyt"
        ],
        "AFRNT"
    ],
    "everyone": [
        "['ev', 'ree', 'wuhn']",
        "AFRN"
    ],
    "everything": [
        "['ev', 'ree', 'thing']",
        "AFR0NK"
    ],
    "everywhere": [
        "['ev', 'ree', 'hwair']",
        "AFRR"
    ],
    "evict": [
        "[ih,vikt]",
        "AFKT"
    ],
    "evicted": [
        "['ih', 'vikt', 'ed']",
        "AFKTT"
    ],
    "evicting": [
        "['ih', 'vikt', 'ing']",
        "AFKTNK"
    ],
    "eviction": [
        "['ih', 'vikt', 'ion']",
        "AFKXN"
    ],
    "evictions": [
        "[ih,vikt,ions]",
        "AFKXNS"
    ],
    "evidence": [
        "[ev,i,duhns]",
        "AFTNS"
    ],
    "evident": [
        "['ev', 'i', 'duhnt']",
        "AFTNT"
    ],
    "evil": [
        "['ee', 'vuhl']",
        "AFL"
    ],
    "evolve": [
        "[ih,volv]",
        "AFLF"
    ],
    "ew": [
        "[ioo]",
        "A"
    ],
    "ex": [
        "['eks']",
        "AKS"
    ],
    "exact": [
        "['ig', 'zakt']",
        "AKSKT"
    ],
    "exactly": [
        "['ig', 'zakt', 'lee']",
        "AKSKTL"
    ],
    "exaggeration": [
        "['ig', 'zaj', 'uh', 'rey', 'shuhn']",
        "AKSKRXN"
    ],
    "exam": [
        "['ig', 'zam']",
        "AKSM"
    ],
    "examine": [
        "[ig,zam,in]",
        "AKSMN"
    ],
    "example": [
        "['ig', 'zam', 'puhl']",
        "AKSMPL"
    ],
    "examples": [
        "[ig,zam,puhl,s]",
        "AKSMPLS"
    ],
    "excellence": [
        "[ek,suh,luhns]",
        "AKSLNS"
    ],
    "excellent": [
        "['ek', 'suh', 'luhnt']",
        "AKSLNT"
    ],
    "except": [
        "['ik', 'sept']",
        "AKSPT"
    ],
    "exception": [
        "[ik,sep,shuhn]",
        "AKSPXN"
    ],
    "excess": [
        "[nounik,ses]",
        "AKSS"
    ],
    "excessive": [
        "[ik,ses,iv]",
        "AKSSF"
    ],
    "exchange": [
        "['iks', 'cheynj']",
        "AKSNJ"
    ],
    "exchanged": [
        "['iks', 'cheynj', 'd']",
        "AKSNJT"
    ],
    "excite": [
        "['ik', 'sahyt']",
        "AKST"
    ],
    "excited": [
        "['ik', 'sahy', 'tid']",
        "AKSTT"
    ],
    "excitement": [
        "[ik,sahyt,muhnt]",
        "AKSTMNT"
    ],
    "exciting": [
        "['ik', 'sahy', 'ting']",
        "AKSTNK"
    ],
    "exclusive": [
        "[ik,skloo,siv]",
        "AKSLSF"
    ],
    "exclusives": [
        "[ik,skloo,siv,s]",
        "AKSLSFS"
    ],
    "excursion": [
        "['ik', 'skur', 'zhuhn']",
        "AKSRSN"
    ],
    "excuse": [
        "['verbik', 'skyooz']",
        "AKSS"
    ],
    "excuses": [
        "[verbik,skyooz,s]",
        "AKSSS"
    ],
    "execute": [
        "[ek,si,kyoot]",
        "AKSKT"
    ],
    "executive": [
        "[ig,zek,yuh,tiv]",
        "AKSKTF"
    ],
    "exercise": [
        "['ek', 'ser', 'sahyz']",
        "AKSRSS"
    ],
    "exes": [
        "['eks', 'es']",
        "AKSS"
    ],
    "exhale": [
        "[eks,heyl]",
        "AKSL"
    ],
    "exhaust": [
        "[ig,zawst]",
        "AKSST"
    ],
    "exhausted": [
        "['ig', 'zawst', 'ed']",
        "AKSSTT"
    ],
    "exhausting": [
        "['ig', 'zaw', 'sting']",
        "AKSSTNK"
    ],
    "exhibit": [
        "[ig,zib,it]",
        "AKSPT"
    ],
    "exist": [
        "[ig,zist]",
        "AKSST"
    ],
    "existed": [
        "['ig', 'zist', 'ed']",
        "AKSSTT"
    ],
    "existence": [
        "['ig', 'zis', 'tuhns']",
        "AKSSTNS"
    ],
    "exists": [
        "[ig,zist,s]",
        "AKSSTS"
    ],
    "exit": [
        "['eg', 'zit']",
        "AKST"
    ],
    "exorcist": [
        "[ek,sawr,sist]",
        "AKSRSST"
    ],
    "exotic": [
        "['ig', 'zot', 'ik']",
        "AKSTK"
    ],
    "expand": [
        "['ik', 'spand']",
        "AKSPNT"
    ],
    "expanded": [
        "['ik', 'span', 'did']",
        "AKSPNTT"
    ],
    "expanding": [
        "['ik', 'spand', 'ing']",
        "AKSPNTNK"
    ],
    "expect": [
        "['ik', 'spekt']",
        "AKSPKT"
    ],
    "expectations": [
        "[ek,spek,tey,shuhn,s]",
        "AKSPKTXNS"
    ],
    "expected": [
        "['ik', 'spekt', 'ed']",
        "AKSPKTT"
    ],
    "expecting": [
        "['ik', 'spekt', 'ing']",
        "AKSPKTNK"
    ],
    "expedition": [
        "[ek,spi,dish,uhn]",
        "AKSPTXN"
    ],
    "expense": [
        "[ik,spens]",
        "AKSPNS"
    ],
    "expenses": [
        "[ik,spens,s]",
        "AKSPNSS"
    ],
    "expensive": [
        "['ik', 'spen', 'siv']",
        "AKSPNSF"
    ],
    "experience": [
        "[ik,speer,ee,uhns]",
        "AKSPRNS"
    ],
    "experiment": [
        "[nounik,sper,uh,muhnt]",
        "AKSPRMNT"
    ],
    "expired": [
        "[ik,spahyuhr,d]",
        "AKSPRT"
    ],
    "explain": [
        "['ik', 'spleyn']",
        "AKSPLN"
    ],
    "explained": [
        "['ik', 'spleyn', 'ed']",
        "AKSPLNT"
    ],
    "explaining": [
        "[ik,spleyn,ing]",
        "AKSPLNNK"
    ],
    "explains": [
        "[ik,spleyn,s]",
        "AKSPLNS"
    ],
    "explanation": [
        "[ek,spluh,ney,shuhn]",
        "AKSPLNXN"
    ],
    "explicit": [
        "['ik', 'splis', 'it']",
        "AKSPLST"
    ],
    "explode": [
        "[ik,splohd]",
        "AKSPLT"
    ],
    "explore": [
        "['ik', 'splawr']",
        "AKSPLR"
    ],
    "explorer": [
        "[ik,splawr,er]",
        "AKSPLRR"
    ],
    "explosive": [
        "[ik,sploh,siv]",
        "AKSPLSF"
    ],
    "export": [
        "[verbik,spawrt]",
        "AKSPRT"
    ],
    "expose": [
        "['ik', 'spohz']",
        "AKSPS"
    ],
    "exposed": [
        "['ik', 'spohzd']",
        "AKSPST"
    ],
    "exposure": [
        "['ik', 'spoh', 'zher']",
        "AKSPSR"
    ],
    "express": [
        "['ik', 'spres']",
        "AKSPRS"
    ],
    "expression": [
        "[ik,spresh,uhn]",
        "AKSPRSN"
    ],
    "expressions": [
        "[ik,spresh,uhn,s]",
        "AKSPRSNS"
    ],
    "exquisite": [
        "['ik', 'skwiz', 'it']",
        "AKSKST"
    ],
    "extend": [
        "[ik,stend]",
        "AKSTNT"
    ],
    "extended": [
        "['ik', 'sten', 'did']",
        "AKSTNTT"
    ],
    "extension": [
        "['ik', 'sten', 'shuhn']",
        "AKSTNSN"
    ],
    "extensions": [
        "['ik', 'sten', 'shuhn', 's']",
        "AKSTNSNS"
    ],
    "extensive": [
        "[ik,sten,siv]",
        "AKSTNSF"
    ],
    "exterior": [
        "['ik', 'steer', 'ee', 'er']",
        "AKSTRR"
    ],
    "extinct": [
        "['ik', 'stingkt']",
        "AKSTNKT"
    ],
    "extorted": [
        "[ik,stawrt,ed]",
        "AKSTRTT"
    ],
    "extorting": [
        "['ik', 'stawrt', 'ing']",
        "AKSTRTNK"
    ],
    "extra": [
        "['ek', 'struh']",
        "AKSTR"
    ],
    "extraordinary": [
        "['ik', 'strawr', 'dn', 'er', 'ee']",
        "AKSTRRTNR"
    ],
    "extras": [
        "[ek,struh,s]",
        "AKSTRS"
    ],
    "extraterrestrial": [
        "[ek,struh,tuh,res,tree,uhl]",
        "AKSTRTRSTRL"
    ],
    "extravagant": [
        "['ik', 'strav', 'uh', 'guhnt']",
        "AKSTRFKNT"
    ],
    "extremely": [
        "[ik,streem,lee]",
        "AKSTRML"
    ],
    "eye": [
        "['ahy']",
        "A"
    ],
    "eye's": [
        "[ahy,'s]",
        "AS"
    ],
    "eyeball": [
        "[ahy,bawl]",
        "APL"
    ],
    "eyeballs": [
        "['ahy', 'bawl', 's']",
        "APLS"
    ],
    "eyebrows": [
        "[ahy,brou,s]",
        "APRS"
    ],
    "eyed": [
        "['ahyd']",
        "AT"
    ],
    "eyeful": [
        "[ahy,fool]",
        "AFL"
    ],
    "eyeing": [
        "['ahy', 'ing']",
        "ANK"
    ],
    "eyelids": [
        "['ahy', 'lid', 's']",
        "ALTS"
    ],
    "eyes": [
        "['ahy', 's']",
        "AS"
    ],
    "eyesight": [
        "[ahy,sahyt]",
        "AST"
    ],
    "f": [
        "['ef', '']",
        "F"
    ],
    "fa": [
        "['fah']",
        "F"
    ],
    "fab": [
        "['fab']",
        "FP"
    ],
    "fable": [
        "[fey,buhl]",
        "FPL"
    ],
    "fabric": [
        "['fab', 'rik']",
        "FPRK"
    ],
    "fabricated": [
        "[fab,ri,keyt,d]",
        "FPRKTT"
    ],
    "fabrics": [
        "['fab', 'rik', 's']",
        "FPRKS"
    ],
    "fabulous": [
        "[fab,yuh,luhs]",
        "FPLS"
    ],
    "facade": [
        "[fuh,sahd]",
        "FKT"
    ],
    "face": [
        "['feys']",
        "FS"
    ],
    "faced": [
        "['feyst']",
        "FST"
    ],
    "faces": [
        "['feys', 's']",
        "FSS"
    ],
    "facial": [
        "['fey', 'shuhl']",
        "FSL"
    ],
    "facility": [
        "['fuh', 'sil', 'i', 'tee']",
        "FSLT"
    ],
    "facing": [
        "['fey', 'sing']",
        "FSNK"
    ],
    "fact": [
        "['fakt']",
        "FKT"
    ],
    "factor": [
        "[fak,ter]",
        "FKTR"
    ],
    "factory": [
        "['fak', 'tuh', 'ree']",
        "FKTR"
    ],
    "facts": [
        "['fakt', 's']",
        "FKTS"
    ],
    "faculty": [
        "[fak,uhl,tee]",
        "FKLT"
    ],
    "fade": [
        "['feyd']",
        "FT"
    ],
    "fadeaway": [
        "['feyd', 'uh', 'wey']",
        "FT"
    ],
    "faded": [
        "['feyd', 'd']",
        "FTT"
    ],
    "fades": [
        "[feyd,s]",
        "FTS"
    ],
    "fag": [
        "[fag]",
        "FK"
    ],
    "faggot": [
        "['fag', 'uht']",
        "FKT"
    ],
    "faggots": [
        "['fag', 'uht', 's']",
        "FKTS"
    ],
    "fags": [
        "[fag,s]",
        "FKS"
    ],
    "fail": [
        "['feyl']",
        "FL"
    ],
    "failed": [
        "[feyld]",
        "FLT"
    ],
    "failing": [
        "['fey', 'ling']",
        "FLNK"
    ],
    "fails": [
        "[feyl,s]",
        "FLS"
    ],
    "failure": [
        "['feyl', 'yer']",
        "FLR"
    ],
    "faint": [
        "['feynt']",
        "FNT"
    ],
    "fainted": [
        "[feynt,ed]",
        "FNTT"
    ],
    "fainting": [
        "['feynt', 'ing']",
        "FNTNK"
    ],
    "fair": [
        "['fair']",
        "FR"
    ],
    "fairy": [
        "['fair', 'ee']",
        "FR"
    ],
    "faith": [
        "['feyth']",
        "F0"
    ],
    "faithful": [
        "['feyth', 'fuhl']",
        "F0FL"
    ],
    "faithfully": [
        "[feyth,fuhl,ly]",
        "F0FL"
    ],
    "fake": [
        "['feyk']",
        "FK"
    ],
    "faked": [
        "[feyk,d]",
        "FKT"
    ],
    "faker": [
        "['fey', 'ker']",
        "FKR"
    ],
    "fakers": [
        "['fey', 'ker', 's']",
        "FKRS"
    ],
    "fakery": [
        "['fey', 'kuh', 'ree']",
        "FKR"
    ],
    "fakes": [
        "['feyk', 's']",
        "FKS"
    ],
    "falcon": [
        "[fawl,kuhn]",
        "FLKN"
    ],
    "falcons": [
        "['fawl', 'kuhn', 's']",
        "FLKNS"
    ],
    "fall": [
        "['fawl']",
        "FL"
    ],
    "fallen": [
        "['faw', 'luhn']",
        "FLN"
    ],
    "falling": [
        "['fawl', 'ing']",
        "FLNK"
    ],
    "fallon": [
        "['fawl', 'on']",
        "FLN"
    ],
    "falls": [
        "['fawlz']",
        "FLS"
    ],
    "false": [
        "['fawls']",
        "FLS"
    ],
    "fam": [
        "['fam']",
        "FM"
    ],
    "fame": [
        "['feym']",
        "FM"
    ],
    "familiar": [
        "['fuh', 'mil', 'yer']",
        "FMLR"
    ],
    "family": [
        "['fam', 'uh', 'lee']",
        "FML"
    ],
    "family's": [
        "[fam,uh,lee,'s]",
        "FMLS"
    ],
    "famous": [
        "['fey', 'muhs']",
        "FMS"
    ],
    "fan": [
        "['fan']",
        "FN"
    ],
    "fanatic": [
        "[fuh,nat,ik]",
        "FNTK"
    ],
    "fancy": [
        "['fan', 'see']",
        "FNS"
    ],
    "fangs": [
        "['fang', 's']",
        "FNKS"
    ],
    "fanny": [
        "['fan', 'ee']",
        "FN"
    ],
    "fans": [
        "['fan', 's']",
        "FNS"
    ],
    "fantasia": [
        "['fan', 'tey', 'zhuh']",
        "FNTS"
    ],
    "fantasize": [
        "['fan', 'tuh', 'sahyz']",
        "FNTSS"
    ],
    "fantastic": [
        "['fan', 'tas', 'tik']",
        "FNTSTK"
    ],
    "fantasy": [
        "['fan', 'tuh', 'see']",
        "FNTS"
    ],
    "far": [
        "['fahr']",
        "FR"
    ],
    "fare": [
        "[fair]",
        "FR"
    ],
    "farewell": [
        "[fair,wel]",
        "FRL"
    ],
    "fargo": [
        "['fahr', 'goh']",
        "FRK"
    ],
    "farm": [
        "['fahrm']",
        "FRM"
    ],
    "farmer": [
        "['fahr', 'mer']",
        "FRMR"
    ],
    "farmers": [
        "['fahr', 'mer', 's']",
        "FRMRS"
    ],
    "fart": [
        "['fahrt']",
        "FRT"
    ],
    "farted": [
        "['fahrt', 'ed']",
        "FRTT"
    ],
    "farther": [
        "['fahr', 'ther']",
        "FR0R"
    ],
    "farting": [
        "['fahrt', 'ing']",
        "FRTNK"
    ],
    "fascinated": [
        "['fas', 'uh', 'neyt', 'd']",
        "FSNTT"
    ],
    "fashion": [
        "['fash', 'uhn']",
        "FXN"
    ],
    "fashioned": [
        "[fash,uhn,ed]",
        "FXNT"
    ],
    "fast": [
        "['fast']",
        "FST"
    ],
    "faster": [
        "['fast', 'er']",
        "FSTR"
    ],
    "fastest": [
        "[fast,est]",
        "FSTST"
    ],
    "fat": [
        "['fat']",
        "FT"
    ],
    "fatal": [
        "[feyt,l]",
        "FTL"
    ],
    "fate": [
        "['feyt']",
        "FT"
    ],
    "father": [
        "['fah', 'ther']",
        "F0R"
    ],
    "father's": [
        "[fah,ther,'s]",
        "F0RRS"
    ],
    "fathered": [
        "['fah', 'ther', 'ed']",
        "F0RT"
    ],
    "fatherless": [
        "[fah,ther,lis]",
        "F0RLS"
    ],
    "fathers": [
        "[fah,ther,s]",
        "F0RS"
    ],
    "fathom": [
        "[fath,uhm]",
        "FTM"
    ],
    "fatigue": [
        "[fuh,teeg]",
        "FTK"
    ],
    "fatigues": [
        "[fuh,teeg,s]",
        "FTKS"
    ],
    "fatter": [
        "['fat', 'ter']",
        "FTR"
    ],
    "fattest": [
        "['fat', 'test']",
        "FTST"
    ],
    "fatty": [
        "[fat,ee]",
        "FT"
    ],
    "faucet": [
        "['faw', 'sit']",
        "FST"
    ],
    "fault": [
        "['fawlt']",
        "FLT"
    ],
    "favor": [
        "['fey', 'ver']",
        "FFR"
    ],
    "favorite": [
        "['fey', 'ver', 'it']",
        "FFRT"
    ],
    "favors": [
        "['fey', 'ver', 's']",
        "FFRS"
    ],
    "favour": [
        "[fey,ver]",
        "FFR"
    ],
    "favours": [
        "[fey,ver,s]",
        "FFRS"
    ],
    "fax": [
        "[faks]",
        "FKS"
    ],
    "fay": [
        "[fey]",
        "F"
    ],
    "faze": [
        "[feyz]",
        "FS"
    ],
    "fdr": [
        "[roh,zuh,velt]",
        "FTR"
    ],
    "fe": [
        "[rn]",
        "F"
    ],
    "fear": [
        "['feer']",
        "FR"
    ],
    "feared": [
        "[feerd]",
        "FRT"
    ],
    "fearing": [
        "[feer,ing]",
        "FRNK"
    ],
    "fearless": [
        "[feer,lis]",
        "FRLS"
    ],
    "fears": [
        "['feer', 's']",
        "FRS"
    ],
    "feast": [
        "['feest']",
        "FST"
    ],
    "feat": [
        "[feet]",
        "FT"
    ],
    "feather": [
        "['feth', 'er']",
        "F0R"
    ],
    "feathers": [
        "['feth', 'er', 's']",
        "F0RS"
    ],
    "feature": [
        "['fee', 'cher']",
        "FTR"
    ],
    "featured": [
        "['fee', 'cherd']",
        "FTRT"
    ],
    "features": [
        "['fee', 'cher', 's']",
        "FTRS"
    ],
    "february": [
        "['feb', 'roo', 'er', 'ee']",
        "FPRR"
    ],
    "fed": [
        "['fed']",
        "FT"
    ],
    "fed's": [
        "['fed', \"'s\"]",
        "FTTS"
    ],
    "federal": [
        "['fed', 'er', 'uhl']",
        "FTRL"
    ],
    "feds": [
        "['fed', 's']",
        "FTS"
    ],
    "fee": [
        "['fee']",
        "F"
    ],
    "feed": [
        "['feed']",
        "FT"
    ],
    "feedback": [
        "['feed', 'bak']",
        "FTPK"
    ],
    "feeding": [
        "['fee', 'ding']",
        "FTNK"
    ],
    "feeds": [
        "['feed', 's']",
        "FTS"
    ],
    "feel": [
        "['feel']",
        "FL"
    ],
    "feeling": [
        "['fee', 'ling']",
        "FLNK"
    ],
    "feeling's": [
        "['fee', 'ling', \"'s\"]",
        "FLNKKS"
    ],
    "feelings": [
        "['fee', 'ling', 's']",
        "FLNKS"
    ],
    "feels": [
        "['feel', 's']",
        "FLS"
    ],
    "fees": [
        "['fee', 's']",
        "FS"
    ],
    "feet": [
        "['feet']",
        "FT"
    ],
    "feigning": [
        "[feyn,ing]",
        "FNNK"
    ],
    "feisty": [
        "[fahy,stee]",
        "FST"
    ],
    "felicia": [
        "['fuh', 'lish', 'uh']",
        "FLS"
    ],
    "feline": [
        "[fee,lahyn]",
        "FLN"
    ],
    "fell": [
        "['fel']",
        "FL"
    ],
    "fellas": [
        "['fel', 'uh', 's']",
        "FLS"
    ],
    "fellatio": [
        "['fuh', 'ley', 'shee', 'oh']",
        "FLT"
    ],
    "feller": [
        "['fel', 'er']",
        "FLR"
    ],
    "felling": [
        "['fel', 'ing']",
        "FLNK"
    ],
    "fellow": [
        "['fel', 'oh']",
        "FL"
    ],
    "fellows": [
        "['fel', 'oh', 's']",
        "FLS"
    ],
    "felon": [
        "['fel', 'uhn']",
        "FLN"
    ],
    "felons": [
        "[fel,uhn,s]",
        "FLNS"
    ],
    "felony": [
        "[fel,uh,nee]",
        "FLN"
    ],
    "felt": [
        "['felt']",
        "FLT"
    ],
    "fema": [
        "[fee,muh]",
        "FM"
    ],
    "female": [
        "['fee', 'meyl']",
        "FML"
    ],
    "females": [
        "[fee,meyl,s]",
        "FMLS"
    ],
    "feminine": [
        "['fem', 'uh', 'nin']",
        "FMNN"
    ],
    "fen": [
        "[fen]",
        "FN"
    ],
    "fence": [
        "['fens']",
        "FNS"
    ],
    "fences": [
        "['fens', 's']",
        "FNSS"
    ],
    "fend": [
        "['fend']",
        "FNT"
    ],
    "fender": [
        "['fen', 'der']",
        "FNTR"
    ],
    "ferris": [
        [
            "fer",
            "ees"
        ],
        "FRS"
    ],
    "fetch": [
        "['fech']",
        "FX"
    ],
    "fetish": [
        "['fet', 'ish']",
        "FTX"
    ],
    "fettuccine": [
        "[fet,uh,chee,nee]",
        "FTXN"
    ],
    "fetus": [
        "[fee,tuhs]",
        "FTS"
    ],
    "feuds": [
        "[fyood,s]",
        "FTS"
    ],
    "fever": [
        "['fee', 'ver']",
        "FFR"
    ],
    "few": [
        "['fyoo']",
        "F"
    ],
    "fiber": [
        "['fahy', 'ber']",
        "FPR"
    ],
    "fiction": [
        "[fik,shuhn]",
        "FKXN"
    ],
    "fiddle": [
        "[fid,l]",
        "FTL"
    ],
    "field": [
        "['feeld']",
        "FLT"
    ],
    "fields": [
        "[feeldz]",
        "FLTS"
    ],
    "fiend": [
        "['feend']",
        "FNT"
    ],
    "fiend's": [
        "[feend,'s]",
        "FNTTS"
    ],
    "fiending": [
        "['feend', 'ing']",
        "FNTNK"
    ],
    "fiends": [
        "['feend', 's']",
        "FNTS"
    ],
    "fierce": [
        "[feers]",
        "FRS"
    ],
    "fifteen": [
        "['fif', 'teen']",
        "FFTN"
    ],
    "fifth": [
        "['fifthor']",
        "FF0"
    ],
    "fifths": [
        "['fifthor', 's']",
        "FF0S"
    ],
    "fifties": [
        [
            "fif",
            "tees"
        ],
        "FFTS"
    ],
    "fifty": [
        "['fif', 'tee']",
        "FFT"
    ],
    "fight": [
        "['fahyt']",
        "FT"
    ],
    "fighter": [
        "['fahy', 'ter']",
        "FTR"
    ],
    "fighters": [
        "[fahy,ter,s]",
        "FTRS"
    ],
    "fighting": [
        "['fahy', 'ting']",
        "FTNK"
    ],
    "fights": [
        "['fahyt', 's']",
        "FTS"
    ],
    "figure": [
        "['fig', 'yer']",
        "FKR"
    ],
    "figured": [
        "['fig', 'yerd']",
        "FKRT"
    ],
    "figures": [
        "['fig', 'yer', 's']",
        "FKRS"
    ],
    "fiji": [
        "['fee', 'jee']",
        "FJ"
    ],
    "file": [
        "[fahyl]",
        "FL"
    ],
    "filer": [
        "[fahyl,r]",
        "FLR"
    ],
    "files": [
        "[fahyl,s]",
        "FLS"
    ],
    "filet": [
        "[fi,ley]",
        "FLT"
    ],
    "filipino": [
        "[fil,uh,pee,noh]",
        "FLPN"
    ],
    "fill": [
        "['fil']",
        "FL"
    ],
    "filled": [
        "['fil', 'ed']",
        "FLT"
    ],
    "filler": [
        "[fil,er]",
        "FLR"
    ],
    "filling": [
        "['fil', 'ing']",
        "FLNK"
    ],
    "fillings": [
        "['fil', 'ing', 's']",
        "FLNKS"
    ],
    "fills": [
        "[fil,s]",
        "FLS"
    ],
    "film": [
        "['film']",
        "FLM"
    ],
    "filter": [
        "['fil', 'ter']",
        "FLTR"
    ],
    "filth": [
        "[filth]",
        "FL0"
    ],
    "filthy": [
        "['fil', 'thee']",
        "FL0"
    ],
    "fin": [
        "[fin]",
        "FN"
    ],
    "final": [
        "['fahyn', 'l']",
        "FNL"
    ],
    "finale": [
        "[fi,nal,ee]",
        "FNL"
    ],
    "finally": [
        "['fahyn', 'l', 'ee']",
        "FNL"
    ],
    "finals": [
        "['fahyn', 'l', 's']",
        "FNLS"
    ],
    "finance": [
        "[fi,nans]",
        "FNNS"
    ],
    "financial": [
        "[fi,nan,shuhl]",
        "FNNSL"
    ],
    "financially": [
        "[fi,nan,shuhl,ly]",
        "FNNSL"
    ],
    "find": [
        "['fahynd']",
        "FNT"
    ],
    "finders": [
        "['fahyn', 'der', 's']",
        "FNTRS"
    ],
    "finding": [
        "['fahyn', 'ding']",
        "FNTNK"
    ],
    "finds": [
        "[fahynd,s]",
        "FNTS"
    ],
    "fine": [
        "['fahyn']",
        "FN"
    ],
    "finer": [
        "['fahy', 'ner']",
        "FNR"
    ],
    "finesse": [
        "['fi', 'ness']",
        "FNS"
    ],
    "finessed": [
        "['fi', 'ness', 'd']",
        "FNST"
    ],
    "finest": [
        "['fahy', 'nist']",
        "FNST"
    ],
    "finger": [
        "['fing', 'ger']",
        "FNKR"
    ],
    "fingernails": [
        "['fing', 'ger', 'neyl', 's']",
        "FNKRNLS"
    ],
    "fingerprints": [
        "[fing,ger,print,s]",
        "FNKRPRNTS"
    ],
    "fingers": [
        "['fing', 'ger', 's']",
        "FNKRS"
    ],
    "fingertips": [
        "[fing,ger,tip,s]",
        "FNKRTPS"
    ],
    "finish": [
        "['fin', 'ish']",
        "FNX"
    ],
    "finished": [
        "['fin', 'isht']",
        "FNXT"
    ],
    "fins": [
        "[fin,s]",
        "FNS"
    ],
    "fire": [
        "['fahyuhr']",
        "FR"
    ],
    "fire's": [
        "[fahyuhr,'s]",
        "FRS"
    ],
    "firearm": [
        "['fahyuhr', 'ahrm']",
        "FRRM"
    ],
    "firecracker": [
        "[fahyuhr,krak,er]",
        "FRKRKR"
    ],
    "fired": [
        "['fahyuhr', 'd']",
        "FRT"
    ],
    "fireman": [
        "['fahyuhr', 'muhn']",
        "FRMN"
    ],
    "fireplace": [
        "['fahyuhr', 'pleys']",
        "FRPLS"
    ],
    "fires": [
        "[fahyuhr,s]",
        "FRS"
    ],
    "firework": [
        "['fahyuhr', 'wurk']",
        "FRRK"
    ],
    "fireworks": [
        "['fahyuhr', 'wurk', 's']",
        "FRRKS"
    ],
    "firing": [
        "['fahyuhr', 'ing']",
        "FRNK"
    ],
    "firm": [
        "['furm']",
        "FRM"
    ],
    "first": [
        "['furst']",
        "FRST"
    ],
    "fish": [
        "['fish']",
        "FX"
    ],
    "fisher": [
        "['fish', 'er']",
        "FXR"
    ],
    "fishes": [
        "['fish', 'es']",
        "FXS"
    ],
    "fishing": [
        "['fish', 'ing']",
        "FXNK"
    ],
    "fishy": [
        "['fish', 'ee']",
        "FX"
    ],
    "fist": [
        "['fist']",
        "FST"
    ],
    "fists": [
        "['fist', 's']",
        "FSTS"
    ],
    "fit": [
        "['fit']",
        "FT"
    ],
    "fitness": [
        "['fit', 'nis']",
        "FTNS"
    ],
    "fits": [
        "['fit', 's']",
        "FTS"
    ],
    "fitted": [
        "['fit', 'id']",
        "FTT"
    ],
    "fittest": [
        "[fit,test]",
        "FTST"
    ],
    "fitting": [
        "['fit', 'ing']",
        "FTNK"
    ],
    "five": [
        "['fahyv']",
        "FF"
    ],
    "fives": [
        "['fahyvz']",
        "FFS"
    ],
    "fix": [
        "['fiks']",
        "FKS"
    ],
    "fixed": [
        "['fikst']",
        "FKST"
    ],
    "fixing": [
        "[fik,sing]",
        "FKSNK"
    ],
    "flag": [
        "['flag']",
        "FLK"
    ],
    "flagging": [
        "['flag', 'ing']",
        "FLJNK"
    ],
    "flagrant": [
        "[fley,gruhnt]",
        "FLKRNT"
    ],
    "flags": [
        "['flag', 's']",
        "FLKS"
    ],
    "flair": [
        "['flair']",
        "FLR"
    ],
    "flake": [
        "['fleyk']",
        "FLK"
    ],
    "flakes": [
        "[fleyk,s]",
        "FLKS"
    ],
    "flame": [
        "['fleym']",
        "FLM"
    ],
    "flamed": [
        "['fleym', 'd']",
        "FLMT"
    ],
    "flames": [
        "['fleym', 's']",
        "FLMS"
    ],
    "flaming": [
        "['fley', 'ming']",
        "FLMNK"
    ],
    "flamingos": [
        "['fluh', 'ming', 'goh', 's']",
        "FLMNKS"
    ],
    "flammable": [
        "[flam,uh,buhl]",
        "FLMPL"
    ],
    "flannel": [
        "[flan,l]",
        "FLNL"
    ],
    "flap": [
        "[flap]",
        "FLP"
    ],
    "flapjack": [
        "[flap,jak]",
        "FLPJK"
    ],
    "flapjacks": [
        "['flap', 'jak', 's']",
        "FLPJKS"
    ],
    "flapping": [
        "[flap,ping]",
        "FLPNK"
    ],
    "flare": [
        "['flair']",
        "FLR"
    ],
    "flaring": [
        "[flair,ing]",
        "FLRNK"
    ],
    "flash": [
        "['flash']",
        "FLX"
    ],
    "flashbacks": [
        "[flash,bak,s]",
        "FLXPKS"
    ],
    "flashed": [
        "[flash,ed]",
        "FLXT"
    ],
    "flashes": [
        "['flash', 'es']",
        "FLXS"
    ],
    "flashing": [
        "['flash', 'ing']",
        "FLXNK"
    ],
    "flashlight": [
        "['flash', 'lahyt']",
        "FLXLT"
    ],
    "flashy": [
        "['flash', 'ee']",
        "FLX"
    ],
    "flat": [
        "['flat']",
        "FLT"
    ],
    "flats": [
        "[flat,s]",
        "FLTS"
    ],
    "flatter": [
        "[flat,er]",
        "FLTR"
    ],
    "flattered": [
        "[flat,er,ed]",
        "FLTRT"
    ],
    "flattery": [
        "[flat,uh,ree]",
        "FLTR"
    ],
    "flaunt": [
        "[flawnt]",
        "FLNT"
    ],
    "flavor": [
        "['fley', 'ver']",
        "FLFR"
    ],
    "flavored": [
        "[fley,ver,ed]",
        "FLFRT"
    ],
    "flavors": [
        "['fley', 'ver', 's']",
        "FLFRS"
    ],
    "flavour": [
        "[fley,ver]",
        "FLFR"
    ],
    "flaw": [
        "['flaw']",
        "FL"
    ],
    "flawless": [
        "['flaw', 'lis']",
        "FLLS"
    ],
    "flaws": [
        "['flaw', 's']",
        "FLS"
    ],
    "flea": [
        "[flee]",
        "FL"
    ],
    "fleas": [
        "['flee', 's']",
        "FLS"
    ],
    "fled": [
        "[fled]",
        "FLT"
    ],
    "flee": [
        "['flee']",
        "FL"
    ],
    "fleece": [
        "['flees']",
        "FLS"
    ],
    "fleeing": [
        "[flee,ing]",
        "FLNK"
    ],
    "fleek": [
        "['fleek']",
        "FLK"
    ],
    "flees": [
        "['flee', 's']",
        "FLS"
    ],
    "fleet": [
        "['fleet']",
        "FLT"
    ],
    "flesh": [
        "['flesh']",
        "FLX"
    ],
    "flew": [
        "['floo']",
        "FL"
    ],
    "flex": [
        "['fleks']",
        "FLKS"
    ],
    "flexed": [
        "['flekst']",
        "FLKST"
    ],
    "flexible": [
        "['flek', 'suh', 'buhl']",
        "FLKSPL"
    ],
    "flexing": [
        "['fleks', 'ing']",
        "FLKSNK"
    ],
    "flick": [
        "['flik']",
        "FLK"
    ],
    "flicking": [
        "['flik', 'ing']",
        "FLKNK"
    ],
    "flicks": [
        "[flik,s]",
        "FLKS"
    ],
    "flier": [
        "['flahy', 'er']",
        "FL"
    ],
    "flight": [
        "['flahyt']",
        "FLT"
    ],
    "flights": [
        "['flahyt', 's']",
        "FLTS"
    ],
    "flinching": [
        "['flinch', 'ing']",
        "FLNXNK"
    ],
    "fling": [
        "['fling']",
        "FLNK"
    ],
    "flip": [
        "['flip']",
        "FLP"
    ],
    "flipped": [
        "['flip', 'ped']",
        "FLPT"
    ],
    "flipper": [
        "['flip', 'er']",
        "FLPR"
    ],
    "flippers": [
        "[flip,er,s]",
        "FLPRS"
    ],
    "flipping": [
        "['flip', 'ing']",
        "FLPNK"
    ],
    "flips": [
        "[flip,s]",
        "FLPS"
    ],
    "flirt": [
        "['flurt']",
        "FLRT"
    ],
    "flirting": [
        "['flurt', 'ing']",
        "FLRTNK"
    ],
    "float": [
        "['floht']",
        "FLT"
    ],
    "floating": [
        "['floh', 'ting']",
        "FLTNK"
    ],
    "floats": [
        "[floht,s]",
        "FLTS"
    ],
    "flock": [
        "['flok']",
        "FLK"
    ],
    "flocking": [
        "['flok', 'ing']",
        "FLKNK"
    ],
    "flocks": [
        "[flok,s]",
        "FLKS"
    ],
    "flood": [
        "['fluhd']",
        "FLT"
    ],
    "flooded": [
        "['fluhd', 'ed']",
        "FLTT"
    ],
    "flooding": [
        "['fluhd', 'ing']",
        "FLTNK"
    ],
    "floor": [
        "['flawr']",
        "FLR"
    ],
    "floors": [
        "['flawr', 's']",
        "FLRS"
    ],
    "flop": [
        "['flop']",
        "FLP"
    ],
    "flops": [
        "['flops']",
        "FLPS"
    ],
    "florist": [
        "['flawr', 'ist']",
        "FLRST"
    ],
    "floss": [
        "['flaws']",
        "FLS"
    ],
    "flossed": [
        "[flaws,ed]",
        "FLST"
    ],
    "flossing": [
        "['flaws', 'ing']",
        "FLSNK"
    ],
    "flossy": [
        "[flaw,see]",
        "FLS"
    ],
    "flounder": [
        "['floun', 'der']",
        "FLNTR"
    ],
    "flour": [
        "['flouuhr']",
        "FLR"
    ],
    "flow": [
        "['floh']",
        "FL"
    ],
    "flow's": [
        "[floh,'s]",
        "FLS"
    ],
    "flower": [
        "['flou', 'er']",
        "FLR"
    ],
    "flowers": [
        "['flou', 'er', 's']",
        "FLRS"
    ],
    "flowing": [
        "['floh', 'ing']",
        "FLNK"
    ],
    "flown": [
        "['flohn']",
        "FLN"
    ],
    "flows": [
        "['floh', 's']",
        "FLS"
    ],
    "floyd": [
        "['floid']",
        "FLT"
    ],
    "flu": [
        "['floo']",
        "FL"
    ],
    "fluent": [
        "['floo', 'uhnt']",
        "FLNT"
    ],
    "fluffy": [
        "['fluhf', 'ee']",
        "FLF"
    ],
    "fluid": [
        "['floo', 'id']",
        "FLT"
    ],
    "fluke": [
        "[flook]",
        "FLK"
    ],
    "flunk": [
        "[fluhngk]",
        "FLNK"
    ],
    "flurry": [
        "['flur', 'ee']",
        "FLR"
    ],
    "flush": [
        "['fluhsh']",
        "FLX"
    ],
    "flushed": [
        "['fluhsh', 'ed']",
        "FLXT"
    ],
    "flushing": [
        "['fluhsh', 'ing']",
        "FLXNK"
    ],
    "flute": [
        "['floot']",
        "FLT"
    ],
    "flutes": [
        "[floot,s]",
        "FLTS"
    ],
    "fly": [
        "['flahy']",
        "FL"
    ],
    "flyer": [
        "['flahy', 'er']",
        "FLR"
    ],
    "flyest": [
        "['flahy', 'est']",
        "FLST"
    ],
    "flying": [
        "['flahy', 'ing']",
        "FLNK"
    ],
    "fo": [
        "['foh']",
        "F"
    ],
    "fo's": [
        "['foh', \"'s\"]",
        "FS"
    ],
    "foam": [
        "['fohm']",
        "FM"
    ],
    "foaming": [
        "[fohm,ing]",
        "FMNK"
    ],
    "focus": [
        "['foh', 'kuhs']",
        "FKS"
    ],
    "focused": [
        "['foh', 'kuhs', 'ed']",
        "FKST"
    ],
    "foe": [
        "['foh']",
        "F"
    ],
    "foes": [
        "['foh', 's']",
        "FS"
    ],
    "fog": [
        "[fog]",
        "FK"
    ],
    "foggy": [
        "[fog,ee]",
        "FK"
    ],
    "foil": [
        "['foil']",
        "FL"
    ],
    "fold": [
        "['fohld']",
        "FLT"
    ],
    "folded": [
        "['fohld', 'ed']",
        "FLTT"
    ],
    "folder": [
        "[fohl,der]",
        "FLTR"
    ],
    "folding": [
        "['fohld', 'ing']",
        "FLTNK"
    ],
    "folds": [
        "[fohld,s]",
        "FLTS"
    ],
    "folk": [
        "['fohk']",
        "FLK"
    ],
    "folks": [
        "['fohk', 's']",
        "FLKS"
    ],
    "follow": [
        "['fol', 'oh']",
        "FL"
    ],
    "followed": [
        "['fol', 'oh', 'ed']",
        "FLT"
    ],
    "followers": [
        "['fol', 'oh', 'er', 's']",
        "FLRS"
    ],
    "following": [
        "['fol', 'oh', 'ing']",
        "FLNK"
    ],
    "follows": [
        "['fol', 'oh', 's']",
        "FLS"
    ],
    "fond": [
        "['fond']",
        "FNT"
    ],
    "food": [
        "['food']",
        "FT"
    ],
    "foods": [
        "[food,s]",
        "FTS"
    ],
    "fool": [
        "['fool']",
        "FL"
    ],
    "fooled": [
        "['fool', 'ed']",
        "FLT"
    ],
    "foolery": [
        "['foo', 'luh', 'ree']",
        "FLR"
    ],
    "fooling": [
        "[fool,ing]",
        "FLNK"
    ],
    "foolish": [
        "['foo', 'lish']",
        "FLX"
    ],
    "foolishness": [
        "[foo,lish,ness]",
        "FLXNS"
    ],
    "fools": [
        "['fool', 's']",
        "FLS"
    ],
    "foot": [
        "['foot']",
        "FT"
    ],
    "footage": [
        "['foot', 'ij']",
        "FTJ"
    ],
    "football": [
        "['foot', 'bawl']",
        "FTPL"
    ],
    "footprints": [
        "[foot,print,s]",
        "FTPRNTS"
    ],
    "foots": [
        "[foot,s]",
        "FTS"
    ],
    "for": [
        "['fawr']",
        "FR"
    ],
    "forbes": [
        "['fawrbz']",
        "FRPS"
    ],
    "force": [
        "['fawrs']",
        "FRS"
    ],
    "forced": [
        "['fawrst']",
        "FRST"
    ],
    "forces": [
        "['fawrs', 's']",
        "FRSS"
    ],
    "ford": [
        "['fawrd']",
        "FRT"
    ],
    "fore": [
        "['fawr']",
        "FR"
    ],
    "forecast": [
        "['fawr', 'kast']",
        "FRKST"
    ],
    "forehead": [
        "[fawr,id]",
        "FRHT"
    ],
    "foreign": [
        "['fawr', 'in']",
        "FRN"
    ],
    "foreigns": [
        [
            "fawr",
            "ins"
        ],
        "FRNS"
    ],
    "foreman": [
        "[fawr,muhn]",
        "FRMN"
    ],
    "forensics": [
        "[fuh,ren,sik,s]",
        "FRNSKS"
    ],
    "foreplay": [
        "['fawr', 'pley']",
        "FRPL"
    ],
    "forest": [
        "['fawr', 'ist']",
        "FRST"
    ],
    "forever": [
        "['fawr', 'ev', 'er']",
        "FRFR"
    ],
    "forewarn": [
        "[fawr,wawrn]",
        "FRRN"
    ],
    "forfeit": [
        "[fawr,fit]",
        "FRFT"
    ],
    "forgave": [
        "[fer,geyv]",
        "FRKF"
    ],
    "forget": [
        "['fer', 'get']",
        "FRKT"
    ],
    "forgetting": [
        "['fer', 'get', 'ting']",
        "FRKTNK"
    ],
    "forgive": [
        "['fer', 'giv']",
        "FRJF"
    ],
    "forgiven": [
        "[fer,giv,n]",
        "FRJFN"
    ],
    "forgiveness": [
        "['fer', 'giv', 'nis']",
        "FRJFNS"
    ],
    "forgiver": [
        "['fer', 'giv', 'r']",
        "FRJFR"
    ],
    "forgiving": [
        "[fer,giv,ing]",
        "FRJFNK"
    ],
    "forgot": [
        "['fer', 'got']",
        "FRKT"
    ],
    "forgotten": [
        "['fer', 'got', 'n']",
        "FRKTN"
    ],
    "fork": [
        "['fawrk']",
        "FRK"
    ],
    "forklift": [
        "['fawrk', 'lift']",
        "FRKLFT"
    ],
    "forks": [
        "['fawrk', 's']",
        "FRKS"
    ],
    "form": [
        "['fawrm']",
        "FRM"
    ],
    "formal": [
        "['fawr', 'muhl']",
        "FRML"
    ],
    "format": [
        "[fawr,mat]",
        "FRMT"
    ],
    "formed": [
        "['fawrm', 'ed']",
        "FRMT"
    ],
    "former": [
        "[fawr,mer]",
        "FRMR"
    ],
    "forms": [
        "[fawrm,s]",
        "FRMS"
    ],
    "formula": [
        "['fawr', 'myuh', 'luh']",
        "FRML"
    ],
    "formulas": [
        "[fawr,myuh,luh,s]",
        "FRMLS"
    ],
    "fornicate": [
        "[fawr,ni,keyt]",
        "FRNKT"
    ],
    "forreal": [
        "['for-', 'ree', 'uhl']",
        "FRL"
    ],
    "fort": [
        "[fawrt]",
        "FRT"
    ],
    "forte": [
        "['fawrt']",
        "FRT"
    ],
    "forth": [
        "['fawrth']",
        "FR0"
    ],
    "fortress": [
        "[fawr,tris]",
        "FRTRS"
    ],
    "forts": [
        "[fawrt,s]",
        "FRTS"
    ],
    "fortunate": [
        "['fawr', 'chuh', 'nit']",
        "FRTNT"
    ],
    "fortune": [
        "['fawr', 'chuhn']",
        "FRTN"
    ],
    "fortunes": [
        "[fawr,chuhn,s]",
        "FRTNS"
    ],
    "forty": [
        "['fawr', 'tee']",
        "FRT"
    ],
    "forward": [
        "['fawr', 'werd']",
        "FRRT"
    ],
    "foster": [
        "[faw,ster]",
        "FSTR"
    ],
    "fought": [
        "['fawt']",
        "FKT"
    ],
    "foul": [
        "['foul']",
        "FL"
    ],
    "found": [
        "['found']",
        "FNT"
    ],
    "foundation": [
        "['foun', 'dey', 'shuhn']",
        "FNTXN"
    ],
    "founder": [
        "[foun,der]",
        "FNTR"
    ],
    "fountain": [
        "[foun,tn]",
        "FNTN"
    ],
    "four": [
        "['fawr']",
        "FR"
    ],
    "four's": [
        "[fawr,'s]",
        "FRRS"
    ],
    "fours": [
        "['fawr', 's']",
        "FRS"
    ],
    "foursome": [
        "[fawr,suhm]",
        "FRSM"
    ],
    "fourteen": [
        "['fawr', 'teen']",
        "FRTN"
    ],
    "fourth": [
        "['fawrth']",
        "FR0"
    ],
    "fowl": [
        "[foul]",
        "FL"
    ],
    "fox": [
        "['foks']",
        "FKS"
    ],
    "foxy": [
        "[fok,see]",
        "FKS"
    ],
    "fraction": [
        "['frak', 'shuhn']",
        "FRKXN"
    ],
    "fragrance": [
        "[frey,gruhns]",
        "FRKRNS"
    ],
    "frail": [
        "[freyl]",
        "FRL"
    ],
    "frame": [
        "['freym']",
        "FRM"
    ],
    "framed": [
        "['freym', 'd']",
        "FRMT"
    ],
    "frames": [
        "['freym', 's']",
        "FRMS"
    ],
    "france": [
        "['frans']",
        "FRNS"
    ],
    "franchise": [
        "[fran,chahyz]",
        "FRNXS"
    ],
    "franck": [
        "['frahngk']",
        "FRNK"
    ],
    "frank": [
        "['frangk']",
        "FRNK"
    ],
    "frankenstein": [
        "['frang', 'kuhn', 'stahyn']",
        "FRNKNSTN"
    ],
    "franklin": [
        "['frangk', 'lin']",
        "FRNKLN"
    ],
    "franklin's": [
        "['frangk', 'lin', \"'s\"]",
        "FRNKLNNS"
    ],
    "franklins": [
        "['frangk', 'lin', 's']",
        "FRNKLNS"
    ],
    "franks": [
        "[frangk,s]",
        "FRNKS"
    ],
    "frat": [
        "['frat']",
        "FRT"
    ],
    "fraud": [
        "['frawd']",
        "FRT"
    ],
    "frauds": [
        "['frawd', 's']",
        "FRTS"
    ],
    "freak": [
        "['freek']",
        "FRK"
    ],
    "freaked": [
        "[freek,ed]",
        "FRKT"
    ],
    "freaking": [
        "['free', 'king']",
        "FRKNK"
    ],
    "freaks": [
        "['freek', 's']",
        "FRKS"
    ],
    "freaky": [
        "['free', 'kee']",
        "FRK"
    ],
    "free": [
        "['free']",
        "FR"
    ],
    "freed": [
        "['free', 'd']",
        "FRT"
    ],
    "freedom": [
        "['free', 'duhm']",
        "FRTM"
    ],
    "freely": [
        "[free,lee]",
        "FRL"
    ],
    "freestyle": [
        "['free', 'stahyl']",
        "FRSTL"
    ],
    "freeway": [
        "['free', 'wey']",
        "FR"
    ],
    "freeze": [
        "['freez']",
        "FRS"
    ],
    "freezer": [
        "['free', 'zer']",
        "FRSR"
    ],
    "freezing": [
        "['free', 'zing']",
        "FRSNK"
    ],
    "french": [
        "['french']",
        "FRNX"
    ],
    "frenzy": [
        "['fren', 'zee']",
        "FRNS"
    ],
    "frequency": [
        "[free,kwuhn,see]",
        "FRKNS"
    ],
    "frequent": [
        "[adjectivefree,kwuhnt]",
        "FRKNT"
    ],
    "fresh": [
        "['fresh']",
        "FRX"
    ],
    "freshen": [
        "[fresh,uhn]",
        "FRXN"
    ],
    "fresher": [
        "['fresh', 'er']",
        "FRXR"
    ],
    "freshest": [
        "['fresh', 'est']",
        "FRXST"
    ],
    "freshly": [
        "[fresh,ly]",
        "FRXL"
    ],
    "freshman": [
        "['fresh', 'muhn']",
        "FRXMN"
    ],
    "fret": [
        "[fret]",
        "FRT"
    ],
    "friction": [
        "[frik,shuhn]",
        "FRKXN"
    ],
    "friday": [
        "['frahy', 'dey']",
        "FRT"
    ],
    "friday's": [
        "[frahy,dey,'s]",
        "FRTS"
    ],
    "fridays": [
        "[frahy,deyz]",
        "FRTS"
    ],
    "fridge": [
        "['frij']",
        "FRJ"
    ],
    "fried": [
        "['frahyd']",
        "FRT"
    ],
    "friend": [
        "['frend']",
        "FRNT"
    ],
    "friend's": [
        "['frend', \"'s\"]",
        "FRNTTS"
    ],
    "friendly": [
        "['frend', 'lee']",
        "FRNTL"
    ],
    "friends": [
        "['frend', 's']",
        "FRNTS"
    ],
    "friendship": [
        "['frend', 'ship']",
        "FRNTXP"
    ],
    "fries": [
        "['frahyz']",
        "FRS"
    ],
    "fright": [
        "['frahyt']",
        "FRT"
    ],
    "frightened": [
        "[frahyt,nd]",
        "FRTNT"
    ],
    "frightening": [
        "['frahyt', 'n', 'ing']",
        "FRTNNK"
    ],
    "frigid": [
        "['frij', 'id']",
        "FRJT"
    ],
    "frigidaire": [
        "['frij', 'i', 'dair']",
        "FRJTR"
    ],
    "frisk": [
        "['frisk']",
        "FRSK"
    ],
    "fro": [
        "['froh']",
        "FR"
    ],
    "frog": [
        "['frog']",
        "FRK"
    ],
    "frogs": [
        "['frog', 's']",
        "FRKS"
    ],
    "from": [
        "['fruhm']",
        "FRM"
    ],
    "front": [
        "['fruhnt']",
        "FRNT"
    ],
    "fronted": [
        "['fruhnt', 'ed']",
        "FRNTT"
    ],
    "fronter": [
        "[fruhn,ter]",
        "FRNTR"
    ],
    "fronting": [
        "['fruhnt', 'ing']",
        "FRNTNK"
    ],
    "fronts": [
        "['fruhnt', 's']",
        "FRNTS"
    ],
    "frost": [
        "['frawst']",
        "FRST"
    ],
    "frostbit": [
        "['frawst', 'bahyt', '']",
        "FRSTPT"
    ],
    "frostbite": [
        "['frawst', 'bahyt']",
        "FRSTPT"
    ],
    "frosted": [
        "['fraw', 'stid']",
        "FRSTT"
    ],
    "frosting": [
        "[fraw,sting]",
        "FRSTNK"
    ],
    "frosty": [
        "['fraw', 'stee']",
        "FRST"
    ],
    "frown": [
        "['froun']",
        "FRN"
    ],
    "froze": [
        "['frohz']",
        "FRS"
    ],
    "frozen": [
        "['froh', 'zuhn']",
        "FRSN"
    ],
    "fruit": [
        "['froot']",
        "FRT"
    ],
    "fruits": [
        "['froot', 's']",
        "FRTS"
    ],
    "fruity": [
        "['froo', 'tee']",
        "FRT"
    ],
    "frustrated": [
        "['fruhs', 'trey', 'tid']",
        "FRSTRTT"
    ],
    "fry": [
        "['frahy']",
        "FR"
    ],
    "frying": [
        "['frahy', 'ing']",
        "FRNK"
    ],
    "fuck": [
        "['fuhk']",
        "FK"
    ],
    "fucked": [
        "['fuhk', 'ed']",
        "FKT"
    ],
    "fucker": [
        "['fuhk', 'er']",
        "FKR"
    ],
    "fuckers": [
        "['fuhk', 'er', 's']",
        "FKRS"
    ],
    "fucking": [
        "['fuhk', 'ing']",
        "FKNK"
    ],
    "fucks": [
        "['fuhk', 's']",
        "FKS"
    ],
    "fuel": [
        "['fyoo', 'uhl']",
        "FL"
    ],
    "fugitive": [
        "[fyoo,ji,tiv]",
        "FJTF"
    ],
    "ful": [
        "[fool]",
        "FL"
    ],
    "fulfill": [
        "[fool,fil]",
        "FLFL"
    ],
    "fulfilled": [
        "['fool', 'fil', 'led']",
        "FLFLT"
    ],
    "fulfilling": [
        "[fool,fil,ling]",
        "FLFLNK"
    ],
    "full": [
        "['fool']",
        "FL"
    ],
    "fuller": [
        "[fool,er]",
        "FLR"
    ],
    "fullest": [
        "[fool,est]",
        "FLST"
    ],
    "fully": [
        "['fool', 'ee']",
        "FL"
    ],
    "fumble": [
        "['fuhm', 'buhl']",
        "FMPL"
    ],
    "fume": [
        "[fyoom]",
        "FM"
    ],
    "fumes": [
        "['fyoom', 's']",
        "FMS"
    ],
    "fun": [
        "['fuhn']",
        "FN"
    ],
    "function": [
        "['fuhngk', 'shuhn']",
        "FNKXN"
    ],
    "fund": [
        "['fuhnd']",
        "FNT"
    ],
    "funds": [
        "['fuhnd', 's']",
        "FNTS"
    ],
    "funeral": [
        "['fyoo', 'ner', 'uhl']",
        "FNRL"
    ],
    "funerals": [
        "[fyoo,ner,uhl,s]",
        "FNRLS"
    ],
    "funk": [
        "['fuhngk']",
        "FNK"
    ],
    "funking": [
        "[fuhngk,ing]",
        "FNKNK"
    ],
    "funky": [
        "['fuhng', 'kee']",
        "FNK"
    ],
    "funny": [
        "['fuhn', 'ee']",
        "FN"
    ],
    "fur": [
        "['fur']",
        "FR"
    ],
    "furious": [
        "['fyoor', 'ee', 'uhs']",
        "FRS"
    ],
    "furnace": [
        "[fur,nis]",
        "FRNS"
    ],
    "furniture": [
        "['fur', 'ni', 'cher']",
        "FRNTR"
    ],
    "furry": [
        "['fur', 'ee']",
        "FR"
    ],
    "furs": [
        "['fur', 's']",
        "FRS"
    ],
    "further": [
        "['fur', 'ther']",
        "FR0R"
    ],
    "furthest": [
        "[fur,thist]",
        "FR0ST"
    ],
    "fuse": [
        "['fyooz']",
        "FS"
    ],
    "fuss": [
        "['fuhs']",
        "FS"
    ],
    "fussing": [
        "[fuhs,ing]",
        "FSNK"
    ],
    "futon": [
        "[foo,ton]",
        "FTN"
    ],
    "futons": [
        "['foo', 'ton', 's']",
        "FTNS"
    ],
    "future": [
        "['fyoo', 'cher']",
        "FTR"
    ],
    "future's": [
        "[fyoo,cher,'s]",
        "FTRS"
    ],
    "futures": [
        "[fyoo,cher,s]",
        "FTRS"
    ],
    "futuristic": [
        "[fyoo,chuh,ris,tik]",
        "FTRSTK"
    ],
    "fuzz": [
        "['fuhz']",
        "FS"
    ],
    "fuzzy": [
        "[fuhz,ee]",
        "FS"
    ],
    "g": [
        "['jee', '']",
        "K"
    ],
    "ga": [
        "['gah']",
        "K"
    ],
    "gadget": [
        "['gaj', 'it']",
        "KJT"
    ],
    "gadgets": [
        "['gaj', 'it', 's']",
        "KJTS"
    ],
    "gag": [
        "['gag']",
        "KK"
    ],
    "gaga": [
        "['gah', 'gah']",
        "KK"
    ],
    "gagging": [
        "['gag', 'ging']",
        "KJNK"
    ],
    "gain": [
        "['geyn']",
        "KN"
    ],
    "gained": [
        "['geyn', 'ed']",
        "KNT"
    ],
    "gaining": [
        "['geyn', 'ing']",
        "KNNK"
    ],
    "gal": [
        "['gal']",
        "KL"
    ],
    "gala": [
        "['gey', 'luh']",
        "KL"
    ],
    "galaxy": [
        "['gal', 'uhk', 'see']",
        "KLKS"
    ],
    "gale": [
        "[geyl]",
        "KL"
    ],
    "gallery": [
        "[gal,uh,ree]",
        "KLR"
    ],
    "gallon": [
        "['gal', 'uhn']",
        "KLN"
    ],
    "galore": [
        "['guh', 'lawr']",
        "KLR"
    ],
    "gals": [
        "[gal,s]",
        "KLS"
    ],
    "gamble": [
        "['gam', 'buhl']",
        "KMPL"
    ],
    "gambling": [
        "['gam', 'bling']",
        "KMPLNK"
    ],
    "game": [
        "['geym']",
        "KM"
    ],
    "game's": [
        "[geym,'s]",
        "KMS"
    ],
    "games": [
        "['geym', 's']",
        "KMS"
    ],
    "gaming": [
        "[gey,ming]",
        "KMNK"
    ],
    "gander": [
        "[gan,der]",
        "KNTR"
    ],
    "gang": [
        "['gang']",
        "KNK"
    ],
    "gangbang": [
        "['gang', 'bang']",
        "KNKPNK"
    ],
    "gangbangers": [
        "['gang', 'bang', 'er', 's']",
        "KNKPNKRS"
    ],
    "gangbanging": [
        "['gang', 'bang', 'ing']",
        "KNKPNJNK"
    ],
    "gangland": [
        "['gang', 'land']",
        "KNKLNT"
    ],
    "gangs": [
        "['gang', 's']",
        "KNKS"
    ],
    "gangster": [
        "['gang', 'ster']",
        "KNKSTR"
    ],
    "gangsters": [
        "['gang', 'ster', 's']",
        "KNKSTRS"
    ],
    "ganja": [
        "['gahn', 'juh']",
        "KNJ"
    ],
    "gap": [
        "[gap]",
        "KP"
    ],
    "gar": [
        "['gahr']",
        "KR"
    ],
    "garage": [
        "['guh', 'rahzh']",
        "KRJ"
    ],
    "garages": [
        "['guh', 'rahzh', 's']",
        "KRJS"
    ],
    "garbage": [
        "[gahr,bij]",
        "KRPJ"
    ],
    "garden": [
        "['gahr', 'dn']",
        "KRTN"
    ],
    "garfield": [
        "['gahr', 'feeld']",
        "KRFLT"
    ],
    "gargle": [
        "[gahr,guhl]",
        "KRKL"
    ],
    "garlic": [
        "['gahr', 'lik']",
        "KRLK"
    ],
    "garment": [
        "[gahr,muhnt]",
        "KRMNT"
    ],
    "garments": [
        "['gahr', 'muhnt', 's']",
        "KRMNTS"
    ],
    "gars": [
        "['gahr', 's']",
        "KRS"
    ],
    "garter": [
        "[gahr,ter]",
        "KRTR"
    ],
    "gary": [
        "[gair,ee]",
        "KR"
    ],
    "gas": [
        "['gas']",
        "KS"
    ],
    "gasoline": [
        "['gas', 'uh', 'leen']",
        "KSLN"
    ],
    "gasping": [
        "[gasp,ing]",
        "KSPNK"
    ],
    "gassed": [
        "['gast']",
        "KST"
    ],
    "gassing": [
        "['gas', 'ing']",
        "KSNK"
    ],
    "gat": [
        "['gat']",
        "KT"
    ],
    "gate": [
        "['geyt']",
        "KT"
    ],
    "gated": [
        "['gey', 'tid']",
        "KTT"
    ],
    "gates": [
        "['geyts']",
        "KTS"
    ],
    "gateway": [
        "[geyt,wey]",
        "KT"
    ],
    "gather": [
        "['gath', 'er']",
        "K0R"
    ],
    "gathered": [
        "[gath,er,ed]",
        "K0RT"
    ],
    "gathering": [
        "[gath,er,ing]",
        "K0RNK"
    ],
    "gator": [
        "['gey', 'ter']",
        "KTR"
    ],
    "gators": [
        "['gey', 'ter', 's']",
        "KTRS"
    ],
    "gats": [
        "['gat', 's']",
        "KTS"
    ],
    "gauge": [
        "['geyj']",
        "KJ"
    ],
    "gave": [
        "['geyv']",
        "KF"
    ],
    "gavel": [
        "['gav', 'uhl']",
        "KFL"
    ],
    "gay": [
        "['gey']",
        "K"
    ],
    "gaze": [
        "[geyz]",
        "KS"
    ],
    "gd": [
        "['gdl', 'n', 'm']",
        "KT"
    ],
    "ge": [
        "['zhey']",
        "J"
    ],
    "gear": [
        "['geer']",
        "JR"
    ],
    "gears": [
        "['geer', 's']",
        "JRS"
    ],
    "gee": [
        "[jee]",
        "J"
    ],
    "geek": [
        "['geek']",
        "JK"
    ],
    "geeked": [
        "['geek', 'ed']",
        "JKT"
    ],
    "geeking": [
        "['geek', 'ing']",
        "JKNK"
    ],
    "gees": [
        "[jee,s]",
        "JS"
    ],
    "geese": [
        "[gees]",
        "JS"
    ],
    "geezer": [
        "['gee', 'zer']",
        "JSR"
    ],
    "geezy": [
        [
            "gee",
            "zee"
        ],
        "JS"
    ],
    "gelatin": [
        "['jel', 'uh', 'tn']",
        "KLTN"
    ],
    "gems": [
        "[gems]",
        "JMS"
    ],
    "general": [
        "[jen,er,uhl]",
        "JNRL"
    ],
    "generally": [
        "[jen,er,uh,lee]",
        "JNRL"
    ],
    "generals": [
        "[jen,er,uhl,s]",
        "JNRLS"
    ],
    "generation": [
        "[jen,uh,rey,shuhn]",
        "JNRXN"
    ],
    "generations": [
        "[jen,uh,rey,shuhn,s]",
        "JNRXNS"
    ],
    "generator": [
        "[jen,uh,rey,ter]",
        "JNRTR"
    ],
    "generous": [
        "[jen,er,uhs]",
        "JNRS"
    ],
    "genes": [
        "['jeen', 's']",
        "JNS"
    ],
    "genesis": [
        "[jen,uh,sis]",
        "JNSS"
    ],
    "genie": [
        "['jee', 'nee']",
        "JN"
    ],
    "genitalia": [
        "[jen,i,tey,lee,uh]",
        "JNTL"
    ],
    "genitals": [
        "[jen,i,tlz]",
        "JNTLS"
    ],
    "genius": [
        "['jeen', 'yuhs']",
        "JNS"
    ],
    "genocide": [
        "[jen,uh,sahyd]",
        "JNST"
    ],
    "gent": [
        "[jent]",
        "JNT"
    ],
    "gentle": [
        "['jen', 'tl']",
        "JNTL"
    ],
    "gentleman": [
        "[jen,tl,muhn]",
        "JNTLMN"
    ],
    "genuine": [
        "['jen', 'yoo', 'in']",
        "JNN"
    ],
    "george": [
        "['jawrj']",
        "JRJ"
    ],
    "georgetown": [
        "[jawrj,toun]",
        "JRKTN"
    ],
    "georgia": [
        "['jawr', 'juh']",
        "JRJ"
    ],
    "germ": [
        "[jurm]",
        "KRM"
    ],
    "german": [
        "['jur', 'muhn']",
        "KRMN"
    ],
    "germans": [
        "[jur,muhn,s]",
        "KRMNS"
    ],
    "germany": [
        "['jur', 'muh', 'nee']",
        "KRMN"
    ],
    "germs": [
        "[jurm,s]",
        "KRMS"
    ],
    "get": [
        "['get']",
        "KT"
    ],
    "gets": [
        "['get', 's']",
        "KTS"
    ],
    "getter": [
        "['get', 'er']",
        "KTR"
    ],
    "getting": [
        "['get', 'ting']",
        "KTNK"
    ],
    "ghana": [
        "['gah', 'nuh']",
        "KN"
    ],
    "ghetto": [
        "['get', 'oh']",
        "KT"
    ],
    "ghettoes": [
        "[get,oh,es]",
        "KTS"
    ],
    "ghettos": [
        "[get,oh,s]",
        "KTS"
    ],
    "ghost": [
        "['gohst']",
        "KST"
    ],
    "ghosts": [
        "['gohsts']",
        "KSTS"
    ],
    "gi": [
        "['gee']",
        "J"
    ],
    "giant": [
        "['jahy', 'uhnt']",
        "JNT"
    ],
    "giants": [
        "[jahy,uhnt,s]",
        "JNTS"
    ],
    "gibbs": [
        "[gibz]",
        "KPS"
    ],
    "gibraltar": [
        "[ji,brawl,ter]",
        "KPRLTR"
    ],
    "gibson": [
        "['gib', 'suhn']",
        "KPSN"
    ],
    "giddy": [
        "[gid,ee]",
        "JT"
    ],
    "gift": [
        "['gift']",
        "JFT"
    ],
    "gifted": [
        "['gif', 'tid']",
        "JFTT"
    ],
    "gifts": [
        "['gift', 's']",
        "JFTS"
    ],
    "gig": [
        "[gig]",
        "JK"
    ],
    "gigantic": [
        "['jahy', 'gan', 'tik']",
        "JKNTK"
    ],
    "giggle": [
        "[gig,uhl]",
        "JKL"
    ],
    "giggles": [
        "[gig,uhl,s]",
        "JKLS"
    ],
    "gilbert": [
        "[gil,bert]",
        "KLPRT"
    ],
    "gimme": [
        "['gim', 'ee']",
        "JM"
    ],
    "gimmick": [
        "['gim', 'ik']",
        "JMK"
    ],
    "gimmicks": [
        "[gim,ik,s]",
        "JMKS"
    ],
    "gin": [
        "[jin]",
        "KN"
    ],
    "ginger": [
        "[jin,jer]",
        "KNKR"
    ],
    "gingerbread": [
        "[jin,jer,bred]",
        "KNKRPRT"
    ],
    "giraffe": [
        "['juh', 'rafor']",
        "JRF"
    ],
    "giraffes": [
        "[juh,rafor,s]",
        "JRFS"
    ],
    "girdle": [
        "[gur,dl]",
        "JRTL"
    ],
    "girl": [
        "['gurl']",
        "JRL"
    ],
    "girl's": [
        "[gurl,'s]",
        "JRLLS"
    ],
    "girlfriend": [
        "['gurl', 'frend']",
        "JRLFRNT"
    ],
    "girlfriend's": [
        "['gurl', 'frend', \"'s\"]",
        "JRLFRNTTS"
    ],
    "girlfriends": [
        "['gurl', 'frend', 's']",
        "JRLFRNTS"
    ],
    "girlies": [
        "['gur', 'lee', 's']",
        "JRLS"
    ],
    "girls": [
        "['gurl', 's']",
        "JRLS"
    ],
    "girly": [
        "['gur', 'lee']",
        "JRL"
    ],
    "git": [
        "[git]",
        "JT"
    ],
    "give": [
        "['giv']",
        "JF"
    ],
    "given": [
        "['giv', 'uhn']",
        "JFN"
    ],
    "givenchy": [
        "['zhi', 'vahn', 'shee']",
        "JFNX"
    ],
    "givens": [
        "[giv,uhn,s]",
        "JFNS"
    ],
    "giver": [
        "[giv,r]",
        "JFR"
    ],
    "gives": [
        "[giv,s]",
        "JFS"
    ],
    "glacier": [
        "['gley', 'sher']",
        "KLS"
    ],
    "glaciers": [
        "['gley', 'sher', 's']",
        "KLSRS"
    ],
    "glad": [
        "['glad']",
        "KLT"
    ],
    "gladiator": [
        "['glad', 'ee', 'ey', 'ter']",
        "KLTTR"
    ],
    "gladly": [
        "[glad,ly]",
        "KLTL"
    ],
    "glamour": [
        "['glam', 'er']",
        "KLMR"
    ],
    "glance": [
        "['glans']",
        "KLNS"
    ],
    "glare": [
        "['glair']",
        "KLR"
    ],
    "glares": [
        "[glair,s]",
        "KLRS"
    ],
    "glaring": [
        "[glair,ing]",
        "KLRNK"
    ],
    "glass": [
        "['glas']",
        "KLS"
    ],
    "glasses": [
        "['glas', 'es']",
        "KLSS"
    ],
    "glassy": [
        "['glas', 'ee']",
        "KLS"
    ],
    "gleam": [
        "['gleem']",
        "KLM"
    ],
    "gleaming": [
        "['gleem', 'ing']",
        "KLMNK"
    ],
    "glee": [
        "[glee]",
        "KL"
    ],
    "glen": [
        "[glen]",
        "KLN"
    ],
    "glide": [
        "['glahyd']",
        "KLT"
    ],
    "glimmer": [
        "[glim,er]",
        "KLMR"
    ],
    "glimpse": [
        "['glimps']",
        "KLMPS"
    ],
    "glisten": [
        "[glis,uhn]",
        "KLSTN"
    ],
    "glistening": [
        "['glis', 'uhn', 'ing']",
        "KLSTNNK"
    ],
    "glitch": [
        "['glich']",
        "KLX"
    ],
    "glitter": [
        "[glit,er]",
        "KLTR"
    ],
    "glitz": [
        "['glits']",
        "KLTS"
    ],
    "global": [
        "['gloh', 'buhl']",
        "KLPL"
    ],
    "globe": [
        "['glohb']",
        "KLP"
    ],
    "glock": [
        [
            "glok"
        ],
        "KLK"
    ],
    "glorify": [
        "[glawr,uh,fahy]",
        "KLRF"
    ],
    "glorious": [
        "[glawr,ee,uhs]",
        "KLRS"
    ],
    "glory": [
        "['glawr', 'ee']",
        "KLR"
    ],
    "gloss": [
        "['glos']",
        "KLS"
    ],
    "glove": [
        "['gluhv']",
        "KLF"
    ],
    "glover": [
        "['gluhv', 'er']",
        "KLFR"
    ],
    "gloves": [
        "['gluhv', 's']",
        "KLFS"
    ],
    "glow": [
        "['gloh']",
        "KL"
    ],
    "glowing": [
        "['gloh', 'ing']",
        "KLNK"
    ],
    "glue": [
        "['gloo']",
        "KL"
    ],
    "glued": [
        "['gloo', 'd']",
        "KLT"
    ],
    "gluteus": [
        "[gloo,tee,uhs]",
        "KLTS"
    ],
    "gnarly": [
        "['nahr', 'lee']",
        "NRL"
    ],
    "gnat": [
        "[nat]",
        "NT"
    ],
    "go": [
        "['goh']",
        "K"
    ],
    "goal": [
        "['gohl']",
        "KL"
    ],
    "goalie": [
        "['goh', 'lee']",
        "KL"
    ],
    "goals": [
        "['gohl', 's']",
        "KLS"
    ],
    "goat": [
        "['goht']",
        "KT"
    ],
    "goblin": [
        "['gob', 'lin']",
        "KPLN"
    ],
    "goblins": [
        "['gob', 'lin', 's']",
        "KPLNS"
    ],
    "god": [
        "['god']",
        "KT"
    ],
    "god's": [
        "['god', \"'s\"]",
        "KTTS"
    ],
    "goddamn": [
        "['god', 'dam']",
        "KTMN"
    ],
    "goddess": [
        "['god', 'is']",
        "KTS"
    ],
    "godfather": [
        "['god', 'fah', 'ther']",
        "KTF0R"
    ],
    "godly": [
        "[god,lee]",
        "KTL"
    ],
    "gods": [
        "['god', 's']",
        "KTS"
    ],
    "godzilla": [
        "['god', 'zil', 'uh']",
        "KTSL"
    ],
    "goes": [
        "['gohz']",
        "KS"
    ],
    "goggles": [
        "['gog', 'uhl', 's']",
        "KKLS"
    ],
    "going": [
        "['goh', 'ing']",
        "KNK"
    ],
    "gold": [
        "['gohld']",
        "KLT"
    ],
    "golden": [
        "['gohl', 'duhn']",
        "KLTN"
    ],
    "goldfish": [
        "[gohld,fish]",
        "KLTFX"
    ],
    "golds": [
        "['gohld', 's']",
        "KLTS"
    ],
    "golf": [
        "['golf']",
        "KLF"
    ],
    "golfer": [
        "['golf', 'er']",
        "KLFR"
    ],
    "golfing": [
        "[golf,ing]",
        "KLFNK"
    ],
    "goliath": [
        "[guh,lahy,uhth]",
        "KL0"
    ],
    "gone": [
        "['gawn']",
        "KN"
    ],
    "goner": [
        "[gaw,ner]",
        "KNR"
    ],
    "gong": [
        "[gawng]",
        "KNK"
    ],
    "gonna": [
        "['gaw', 'nuh']",
        "KN"
    ],
    "gonzales": [
        "['guhn', 'zah', 'lis']",
        "KNSLS"
    ],
    "goo": [
        "['goo']",
        "K"
    ],
    "good": [
        "['good']",
        "KT"
    ],
    "goodbye": [
        "['good', 'bahy']",
        "KTP"
    ],
    "goodbyes": [
        "['good', 'bahy', 's']",
        "KTPS"
    ],
    "goodie": [
        "['good', 'ee']",
        "KT"
    ],
    "goodies": [
        "[good,ee,s]",
        "KTS"
    ],
    "goodness": [
        "[good,nis]",
        "KTNS"
    ],
    "goods": [
        "[good,s]",
        "KTS"
    ],
    "goody": [
        "[good,ee]",
        "KT"
    ],
    "gooey": [
        "[goo,ee]",
        "K"
    ],
    "goof": [
        "['goof']",
        "KF"
    ],
    "goofy": [
        "['goo', 'fee']",
        "KF"
    ],
    "google": [
        "['goo', 'guhl']",
        "KKL"
    ],
    "goon": [
        "['goon']",
        "KN"
    ],
    "goonies": [
        [
            "goon",
            "ees"
        ],
        "KNS"
    ],
    "goons": [
        "['goon', 's']",
        "KNS"
    ],
    "goose": [
        "['goos']",
        "KS"
    ],
    "gorgeous": [
        "['gawr', 'juhs']",
        "KRJS"
    ],
    "gorilla": [
        "['guh', 'ril', 'uh']",
        "KRL"
    ],
    "gorillas": [
        "[guh,ril,uh,s]",
        "KRLS"
    ],
    "gospel": [
        "[gos,puhl]",
        "KSPL"
    ],
    "gossip": [
        "[gos,uhp]",
        "KSP"
    ],
    "gossiping": [
        "[gos,uhp,ing]",
        "KSPNK"
    ],
    "got": [
        "['got']",
        "KT"
    ],
    "gotcha": [
        "['goch', 'uh']",
        "KX"
    ],
    "gotta": [
        "['got', 'uh']",
        "KT"
    ],
    "gotten": [
        "['got', 'n']",
        "KTN"
    ],
    "gotti": [
        [
            "got",
            "tee"
        ],
        "KT"
    ],
    "government": [
        "[guhv,ern,muhnt]",
        "KFRNMNT"
    ],
    "governor": [
        "['guhv', 'er', 'ner']",
        "KFRNR"
    ],
    "gown": [
        "['goun']",
        "KN"
    ],
    "gowned": [
        "[goun,ed]",
        "KNT"
    ],
    "grab": [
        "['grab']",
        "KRP"
    ],
    "grabbed": [
        "['grab', 'bed']",
        "KRPT"
    ],
    "grabbing": [
        "['grab', 'bing']",
        "KRPNK"
    ],
    "grace": [
        "['greys']",
        "KRS"
    ],
    "gracious": [
        "[grey,shuhs]",
        "KRSS"
    ],
    "grade": [
        "['greyd']",
        "KRT"
    ],
    "grades": [
        "['greyd', 's']",
        "KRTS"
    ],
    "graduate": [
        "['noun']",
        "KRTT"
    ],
    "graduated": [
        "['graj', 'oo', 'ey', 'tid']",
        "KRTTT"
    ],
    "graduation": [
        "['graj', 'oo', 'ey', 'shuhn']",
        "KRTXN"
    ],
    "graffiti": [
        "[gruh,fee,tee]",
        "KRFT"
    ],
    "graham": [
        "[grey,uhm]",
        "KRHM"
    ],
    "grain": [
        "['greyn']",
        "KRN"
    ],
    "gram": [
        "['gram']",
        "KRM"
    ],
    "grammar": [
        "['gram', 'er']",
        "KRMR"
    ],
    "grammy": [
        "['gram', 'ee']",
        "KRM"
    ],
    "grammy's": [
        "['gram', 'ee', \"'s\"]",
        "KRMS"
    ],
    "grams": [
        "['gram', 's']",
        "KRMS"
    ],
    "gran": [
        "[gran]",
        "KRN"
    ],
    "grand": [
        "['grand']",
        "KRNT"
    ],
    "granddaddy": [
        "['gran', 'dad', 'ee']",
        "KRNTT"
    ],
    "grande": [
        "['grand']",
        "KRNT"
    ],
    "grandfather": [
        "[gran,fah,ther]",
        "KRNTF0R"
    ],
    "grandma": [
        "['gran', 'mah']",
        "KRNTM"
    ],
    "grandma's": [
        "['gran', 'mah', \"'s\"]",
        "KRNTMS"
    ],
    "grandmother": [
        "['gran', 'muhth', 'er']",
        "KRNTM0R"
    ],
    "grandmother's": [
        "['gran', 'muhth', 'er', \"'s\"]",
        "KRNTM0RRS"
    ],
    "grandpa": [
        "[gran,pah]",
        "KRNTP"
    ],
    "grands": [
        "[grand,s]",
        "KRNTS"
    ],
    "grandson": [
        "['gran', 'suhn']",
        "KRNTSN"
    ],
    "granny": [
        "['gran', 'ee']",
        "KRN"
    ],
    "granny's": [
        "['gran', 'ee', \"'s\"]",
        "KRNS"
    ],
    "grant": [
        "['grant']",
        "KRNT"
    ],
    "granted": [
        "['grant', 'ed']",
        "KRNTT"
    ],
    "granting": [
        "['grant', 'ing']",
        "KRNTNK"
    ],
    "grants": [
        "[grants]",
        "KRNTS"
    ],
    "grape": [
        "['greyp']",
        "KRP"
    ],
    "grapes": [
        "['greyp', 's']",
        "KRPS"
    ],
    "grapevine": [
        "[greyp,vahyn]",
        "KRPFN"
    ],
    "graphic": [
        "['graf', 'ik']",
        "KRFK"
    ],
    "grasp": [
        "[grasp]",
        "KRSP"
    ],
    "grass": [
        "['gras']",
        "KRS"
    ],
    "grateful": [
        "[greyt,fuhl]",
        "KRTFL"
    ],
    "gratitude": [
        "[grat,i,tood]",
        "KRTTT"
    ],
    "grave": [
        "['greyv']",
        "KRF"
    ],
    "gravel": [
        "[grav,uhl]",
        "KRFL"
    ],
    "graveyard": [
        "['greyv', 'yahrd']",
        "KRFRT"
    ],
    "gravitate": [
        "[grav,i,teyt]",
        "KRFTT"
    ],
    "gravity": [
        "[grav,i,tee]",
        "KRFT"
    ],
    "gravity's": [
        "[grav,i,tee,'s]",
        "KRFTS"
    ],
    "gravy": [
        "['grey', 'vee']",
        "KRF"
    ],
    "gray": [
        "[grey]",
        "KR"
    ],
    "graze": [
        "[greyz]",
        "KRS"
    ],
    "grease": [
        "['noungrees']",
        "KRS"
    ],
    "greasy": [
        "[gree,see]",
        "KRS"
    ],
    "great": [
        "['greyt']",
        "KRT"
    ],
    "greater": [
        "[grey,ter]",
        "KRTR"
    ],
    "greatest": [
        "['greyt', 'est']",
        "KRTST"
    ],
    "greatness": [
        "['greyt', 'ness']",
        "KRTNS"
    ],
    "greats": [
        "[greyt,s]",
        "KRTS"
    ],
    "greece": [
        "[grees]",
        "KRS"
    ],
    "greed": [
        "['greed']",
        "KRT"
    ],
    "greedy": [
        "['gree', 'dee']",
        "KRT"
    ],
    "greek": [
        "[greek]",
        "KRK"
    ],
    "green": [
        "['green']",
        "KRN"
    ],
    "greener": [
        "['green', 'er']",
        "KRNR"
    ],
    "greenery": [
        "[gree,nuh,ree]",
        "KRNR"
    ],
    "greens": [
        "['green', 's']",
        "KRNS"
    ],
    "greet": [
        "['greet']",
        "KRT"
    ],
    "greeted": [
        "[greet,ed]",
        "KRTT"
    ],
    "greeting": [
        "[gree,ting]",
        "KRTNK"
    ],
    "grenade": [
        "[gri,neyd]",
        "KRNT"
    ],
    "grenades": [
        "[gri,neyd,s]",
        "KRNTS"
    ],
    "gresham": [
        "['gresh', 'uhm']",
        "KRXM"
    ],
    "grew": [
        "['groo']",
        "KR"
    ],
    "grey": [
        "['grey']",
        "KR"
    ],
    "greyhound": [
        "[grey,hound]",
        "KRHNT"
    ],
    "grid": [
        "[grid]",
        "KRT"
    ],
    "grief": [
        "[greef]",
        "KRF"
    ],
    "grieve": [
        "['greev']",
        "KRF"
    ],
    "griffin": [
        "['grif', 'in']",
        "KRFN"
    ],
    "grill": [
        "['gril']",
        "KRL"
    ],
    "grilling": [
        "[gril,ing]",
        "KRLNK"
    ],
    "grills": [
        "['gril', 's']",
        "KRLS"
    ],
    "grim": [
        "['grim']",
        "KRM"
    ],
    "grime": [
        "[grahym]",
        "KRM"
    ],
    "grimy": [
        "['grahy', 'mee']",
        "KRM"
    ],
    "grin": [
        "['grin']",
        "KRN"
    ],
    "grinch": [
        "['grinch']",
        "KRNX"
    ],
    "grind": [
        "['grahynd']",
        "KRNT"
    ],
    "grinder": [
        "[grahyn,der]",
        "KRNTR"
    ],
    "grinding": [
        "['grahynd', 'ing']",
        "KRNTNK"
    ],
    "gringo": [
        "['gring', 'goh']",
        "KRNK"
    ],
    "gringos": [
        "['gring', 'goh', 's']",
        "KRNKS"
    ],
    "grinning": [
        "['grin', 'ning']",
        "KRNNK"
    ],
    "grip": [
        "['grip']",
        "KRP"
    ],
    "gripping": [
        "['grip', 'ing']",
        "KRPNK"
    ],
    "grips": [
        "[grip,s]",
        "KRPS"
    ],
    "grits": [
        "['grits']",
        "KRTS"
    ],
    "gritting": [
        "[grit,ting]",
        "KRTNK"
    ],
    "gritty": [
        "[grit,ee]",
        "KRT"
    ],
    "grizzle": [
        "[griz,uhl]",
        "KRSL"
    ],
    "grizzles": [
        "[griz,uhl,s]",
        "KRSLS"
    ],
    "grizzly": [
        "[griz,lee]",
        "KRSL"
    ],
    "grocery": [
        "['groh', 'suh', 'ree']",
        "KRSR"
    ],
    "groom": [
        "['groom']",
        "KRM"
    ],
    "groove": [
        "['groov']",
        "KRF"
    ],
    "grooves": [
        "[groov,s]",
        "KRFS"
    ],
    "groovy": [
        "[groo,vee]",
        "KRF"
    ],
    "gross": [
        "['grohs']",
        "KRS"
    ],
    "grossed": [
        "[grohs,ed]",
        "KRST"
    ],
    "ground": [
        "['ground']",
        "KRNT"
    ],
    "grounded": [
        "['ground', 'ed']",
        "KRNTT"
    ],
    "grounds": [
        "[ground,s]",
        "KRNTS"
    ],
    "group": [
        "['groop']",
        "KRP"
    ],
    "groupie": [
        "['groo', 'pee']",
        "KRP"
    ],
    "groupies": [
        "['groo', 'pee', 's']",
        "KRPS"
    ],
    "groups": [
        "[groop,s]",
        "KRPS"
    ],
    "grove": [
        "['grohv']",
        "KRF"
    ],
    "grow": [
        "['groh']",
        "KR"
    ],
    "growing": [
        "['groh', 'ing']",
        "KRNK"
    ],
    "growling": [
        "[groul,ing]",
        "KRLNK"
    ],
    "grown": [
        "['grohn']",
        "KRN"
    ],
    "grows": [
        "[groh,s]",
        "KRS"
    ],
    "growth": [
        "['grohth']",
        "KR0"
    ],
    "grub": [
        "[gruhb]",
        "KRP"
    ],
    "grudge": [
        "[gruhj]",
        "KRJ"
    ],
    "grudges": [
        "[gruhj,s]",
        "KRJS"
    ],
    "grunge": [
        "[gruhnj]",
        "KRNJ"
    ],
    "gs": [
        "['jee']",
        "KS"
    ],
    "gu": [
        [
            "jee",
            "yoo"
        ],
        "K"
    ],
    "guacamole": [
        "['gwah', 'kuh', 'moh', 'lee']",
        "KKML"
    ],
    "guarantee": [
        "['gar', 'uhn', 'tee']",
        "KRNT"
    ],
    "guaranteed": [
        "[gar,uhn,tee,d]",
        "KRNTT"
    ],
    "guard": [
        "['gahrd']",
        "KRT"
    ],
    "guardian": [
        "[gahr,dee,uhn]",
        "KRTN"
    ],
    "guarding": [
        "[gahrd,ing]",
        "KRTNK"
    ],
    "guards": [
        "['gahrd', 's']",
        "KRTS"
    ],
    "gucci": [
        [
            "goo",
            "chee"
        ],
        "KX"
    ],
    "guerilla": [
        "[guh,ril,uh]",
        "KRL"
    ],
    "guerillas": [
        "[guh,ril,uh,s]",
        "KRLS"
    ],
    "guerrilla": [
        "[guh,ril,uh]",
        "KRL"
    ],
    "guess": [
        "['ges']",
        "KS"
    ],
    "guessed": [
        "[ges,ed]",
        "KST"
    ],
    "guessing": [
        "['ges', 'ing']",
        "KSNK"
    ],
    "guest": [
        "['gest']",
        "KST"
    ],
    "guests": [
        "['gest', 's']",
        "KSTS"
    ],
    "guevara": [
        "[guh,vahr,uh]",
        "KFR"
    ],
    "guidance": [
        "['gahyd', 'ns']",
        "KTNS"
    ],
    "guide": [
        "['gahyd']",
        "KT"
    ],
    "guillotine": [
        "['gil', 'uh', 'teen']",
        "KLTN"
    ],
    "guilt": [
        "['gilt']",
        "KLT"
    ],
    "guilty": [
        "['gil', 'tee']",
        "KLT"
    ],
    "guinness": [
        "['gin', 'is']",
        "KNS"
    ],
    "guitar": [
        "['gi', 'tahr']",
        "KTR"
    ],
    "guitars": [
        "[gi,tahr,s]",
        "KTRS"
    ],
    "gullible": [
        "[guhl,uh,buhl]",
        "KLPL"
    ],
    "gully": [
        "[guhl,ee]",
        "KL"
    ],
    "gum": [
        "['guhm']",
        "KM"
    ],
    "gumbo": [
        "['guhm', 'boh']",
        "KMP"
    ],
    "gummy": [
        "[guhm,ee]",
        "KM"
    ],
    "gums": [
        "[guhm,s]",
        "KMS"
    ],
    "gun": [
        "['guhn']",
        "KN"
    ],
    "gunfight": [
        "[guhn,fahyt]",
        "KNFT"
    ],
    "gunfire": [
        "[guhn,fahyuhr]",
        "KNFR"
    ],
    "gunned": [
        "[guhn,ned]",
        "KNT"
    ],
    "gunner": [
        "['guhn', 'er']",
        "KNR"
    ],
    "gunners": [
        "['guhn', 'er', 's']",
        "KNRS"
    ],
    "gunning": [
        "['guhn', 'ing']",
        "KNNK"
    ],
    "gunplay": [
        "['guhn', 'pley']",
        "KNPL"
    ],
    "guns": [
        "['guhn', 's']",
        "KNS"
    ],
    "gunshot": [
        "[guhn,shot]",
        "KNXT"
    ],
    "gunshots": [
        "[guhn,shot,s]",
        "KNXTS"
    ],
    "guru": [
        "[goor,oo]",
        "KR"
    ],
    "gushing": [
        "['guhsh', 'ing']",
        "KXNK"
    ],
    "gushy": [
        "['guhsh', 'ee']",
        "KX"
    ],
    "gut": [
        "['guht']",
        "KT"
    ],
    "guts": [
        "['guht', 's']",
        "KTS"
    ],
    "gutter": [
        "['guht', 'er']",
        "KTR"
    ],
    "guy": [
        "['gahy']",
        "K"
    ],
    "guys": [
        "['gahy', 's']",
        "KS"
    ],
    "gym": [
        "['jim']",
        "KM"
    ],
    "gymnastics": [
        "['jim', 'nas', 'tiks']",
        "KMNSTKS"
    ],
    "gynecologist": [
        "[gahy,ni,kol,uh,jist]",
        "KNKLJST"
    ],
    "gypsy": [
        "[jip,see]",
        "KPS"
    ],
    "h": [
        "['eych', '']",
        ""
    ],
    "ha": [
        "['hah']",
        "H"
    ],
    "habit": [
        "['hab', 'it']",
        "HPT"
    ],
    "habitat": [
        "[hab,i,tat]",
        "HPTT"
    ],
    "habits": [
        "['hab', 'it', 's']",
        "HPTS"
    ],
    "hack": [
        "['hak']",
        "HK"
    ],
    "hacking": [
        "[hak,ing]",
        "HKNK"
    ],
    "had": [
        "['had']",
        "HT"
    ],
    "hail": [
        "['heyl']",
        "HL"
    ],
    "hailing": [
        "[heyl,ing]",
        "HLNK"
    ],
    "hair": [
        "['hair']",
        "HR"
    ],
    "hair's": [
        "['hair', \"'s\"]",
        "HRRS"
    ],
    "haircut": [
        "['hair', 'kuht']",
        "HRKT"
    ],
    "haired": [
        "[haird]",
        "HRT"
    ],
    "hairline": [
        "[hair,lahyn]",
        "HRLN"
    ],
    "hairpin": [
        "[hair,pin]",
        "HRPN"
    ],
    "hairs": [
        "[hair,s]",
        "HRS"
    ],
    "hairy": [
        "['hair', 'ee']",
        "HR"
    ],
    "haiti": [
        "['hey', 'tee']",
        "HT"
    ],
    "haitian": [
        "['hey', 'shuhn']",
        "HXN"
    ],
    "haitians": [
        "['hey', 'shuhn', 's']",
        "HXNS"
    ],
    "haley": [
        "[hey,lee]",
        "HL"
    ],
    "half": [
        "['haf']",
        "HLF"
    ],
    "halftime": [
        "['haf', 'tahym']",
        "HLFTM"
    ],
    "halfway": [
        "[haf,wey]",
        "HLF"
    ],
    "hall": [
        "['hawl']",
        "HL"
    ],
    "halle": [
        "['hal', 'eefor1']",
        "HL"
    ],
    "hallelujah": [
        "['hal', 'uh', 'loo', 'yuh']",
        "HLLJ"
    ],
    "hallmark": [
        "[hawl,mahrk]",
        "HLMRK"
    ],
    "hallow": [
        "[hal,oh]",
        "HL"
    ],
    "halloween": [
        "['hal', 'uh', 'ween']",
        "HLN"
    ],
    "halls": [
        "['hawl', 's']",
        "HLS"
    ],
    "hallway": [
        "['hawl', 'wey']",
        "HL"
    ],
    "hallways": [
        "['hawl', 'wey', 's']",
        "HLS"
    ],
    "halo": [
        "[hey,loh]",
        "HL"
    ],
    "halt": [
        "[hawlt]",
        "HLT"
    ],
    "halves": [
        "['havz']",
        "HLFS"
    ],
    "ham": [
        "['ham']",
        "HM"
    ],
    "hamburger": [
        "[ham,bur,ger]",
        "HMPRKR"
    ],
    "hammer": [
        "['ham', 'er']",
        "HMR"
    ],
    "hammered": [
        "['ham', 'erd']",
        "HMRT"
    ],
    "hammers": [
        "['ham', 'er', 's']",
        "HMRS"
    ],
    "hammock": [
        "[ham,uhk]",
        "HMK"
    ],
    "hammy": [
        "[ham,ee]",
        "HM"
    ],
    "hamper": [
        "[ham,per]",
        "HMPR"
    ],
    "hampton": [
        "[hamp,tuhn]",
        "HMPTN"
    ],
    "hamptons": [
        "['hamp', 'tuhn', 's']",
        "HMPTNS"
    ],
    "han": [
        "[hahn]",
        "HN"
    ],
    "hand": [
        "['hand']",
        "HNT"
    ],
    "handcuff": [
        "[hand,kuhf]",
        "HNTKF"
    ],
    "handcuffs": [
        "['hand', 'kuhf', 's']",
        "HNTKFS"
    ],
    "handed": [
        "['han', 'did']",
        "HNTT"
    ],
    "handful": [
        "['hand', 'fool']",
        "HNTFL"
    ],
    "handgun": [
        "['hand', 'guhn']",
        "HNTKN"
    ],
    "handing": [
        "[hand,ing]",
        "HNTNK"
    ],
    "handkerchief": [
        "[hang,ker,chif]",
        "HNTKRXF"
    ],
    "handle": [
        "['han', 'dl']",
        "HNTL"
    ],
    "handled": [
        "['han', 'dld']",
        "HNTLT"
    ],
    "handles": [
        "['han', 'dl', 's']",
        "HNTLS"
    ],
    "handling": [
        "['hand', 'ling']",
        "HNTLNK"
    ],
    "handmade": [
        "[hand,meyd]",
        "HNTMT"
    ],
    "handout": [
        "[hand,out]",
        "HNTT"
    ],
    "handouts": [
        "[hand,out,s]",
        "HNTTS"
    ],
    "hands": [
        "['hand', 's']",
        "HNTS"
    ],
    "handshakes": [
        "[hand,sheyk,s]",
        "HNTXKS"
    ],
    "handsome": [
        "['han', 'suhm']",
        "HNTSM"
    ],
    "handstand": [
        "['hand', 'stand']",
        "HNTSTNT"
    ],
    "handy": [
        "['han', 'dee']",
        "HNT"
    ],
    "hang": [
        "['hang']",
        "HNK"
    ],
    "hangers": [
        "['hang', 'er', 's']",
        "HNKRS"
    ],
    "hanging": [
        "['hang', 'ing']",
        "HNJNK"
    ],
    "hangover": [
        "[hang,oh,ver]",
        "HNKFR"
    ],
    "hangs": [
        "[hang,s]",
        "HNKS"
    ],
    "hank": [
        "[hangk]",
        "HNK"
    ],
    "hanks": [
        "[hangks]",
        "HNKS"
    ],
    "hanna": [
        "['han', 'uh']",
        "HN"
    ],
    "hannah": [
        "['han', 'uh']",
        "HN"
    ],
    "hannibal": [
        "['han', 'uh', 'buhl']",
        "HNPL"
    ],
    "hap": [
        "[hap]",
        "HP"
    ],
    "happen": [
        "['hap', 'uhn']",
        "HPN"
    ],
    "happened": [
        "['hap', 'uhn', 'ed']",
        "HPNT"
    ],
    "happening": [
        "['hap', 'uh', 'ning']",
        "HPNNK"
    ],
    "happens": [
        "['hap', 'uhn', 's']",
        "HPNS"
    ],
    "happily": [
        "[hap,uh,lee]",
        "HPL"
    ],
    "happiness": [
        "['hap', 'ee', 'nis']",
        "HPNS"
    ],
    "happy": [
        "['hap', 'ee']",
        "HP"
    ],
    "harassing": [
        "[huh,ras,ing]",
        "HRSNK"
    ],
    "harbor": [
        "['hahr', 'ber']",
        "HRPR"
    ],
    "hard": [
        "['hahrd']",
        "HRT"
    ],
    "harden": [
        "['hahr', 'dn']",
        "HRTN"
    ],
    "harder": [
        "['hahrd', 'er']",
        "HRTR"
    ],
    "hardest": [
        "['hahrd', 'est']",
        "HRTST"
    ],
    "hardly": [
        "['hahrd', 'lee']",
        "HRTL"
    ],
    "hardtop": [
        "['hahrd', 'top']",
        "HRTP"
    ],
    "hardwood": [
        "['hahrd', 'wood']",
        "HRTT"
    ],
    "hare": [
        "[hair]",
        "HR"
    ],
    "harlem": [
        "['hahr', 'luhm']",
        "HRLM"
    ],
    "harlem's": [
        "[hahr,luhm,'s]",
        "HRLMMS"
    ],
    "harley": [
        "['hahr', 'lee']",
        "HRL"
    ],
    "harm": [
        "['hahrm']",
        "HRM"
    ],
    "harming": [
        "[hahrm,ing]",
        "HRMNK"
    ],
    "harmony": [
        "[hahr,muh,nee]",
        "HRMN"
    ],
    "harry": [
        "[har,ee]",
        "HR"
    ],
    "harsh": [
        "[hahrsh]",
        "HRX"
    ],
    "hart": [
        "['hahrt']",
        "HRT"
    ],
    "harvard": [
        "['hahr', 'verd']",
        "HRFRT"
    ],
    "harvest": [
        "['hahr', 'vist']",
        "HRFST"
    ],
    "harvey": [
        "['hahr', 'vee']",
        "HRF"
    ],
    "has": [
        "['haz']",
        "HS"
    ],
    "hash": [
        "['hash']",
        "HX"
    ],
    "hashtag": [
        "['hash', 'tag']",
        "HXTK"
    ],
    "hasn't": [
        "['haz', 'uhnt']",
        "HSNNT"
    ],
    "hasty": [
        "[hey,stee]",
        "HST"
    ],
    "hat": [
        "['hat']",
        "HT"
    ],
    "hatch": [
        "['hach']",
        "HX"
    ],
    "hate": [
        "['heyt']",
        "HT"
    ],
    "hated": [
        "['heyt', 'd']",
        "HTT"
    ],
    "hater": [
        "['hey', 'ter']",
        "HTR"
    ],
    "hater's": [
        "['hey', 'ter', \"'s\"]",
        "HTRRS"
    ],
    "haters": [
        "['hey', 'ter', 's']",
        "HTRS"
    ],
    "hates": [
        "[heyt,s]",
        "HTS"
    ],
    "hatred": [
        "['hey', 'trid']",
        "HTRT"
    ],
    "hats": [
        "[hat,s]",
        "HTS"
    ],
    "haul": [
        "[hawl]",
        "HL"
    ],
    "haunt": [
        "[hawnt]",
        "HNT"
    ],
    "haunted": [
        "[hawn,tid]",
        "HNTT"
    ],
    "haunting": [
        "['hawn', 'ting']",
        "HNTNK"
    ],
    "havana": [
        "['huh', 'van', 'uh']",
        "HFN"
    ],
    "have": [
        "['hav']",
        "HF"
    ],
    "haven": [
        "[hey,vuhn]",
        "HFN"
    ],
    "haven't": [
        "['hav', 'uhnt']",
        "HFNNT"
    ],
    "having": [
        [
            "hav",
            "ing"
        ],
        "HFNK"
    ],
    "havoc": [
        "[hav,uhk]",
        "HFK"
    ],
    "haw": [
        "['haw']",
        "H"
    ],
    "hawaii": [
        "['huh', 'wahy', 'ee']",
        "H"
    ],
    "hawaiian": [
        "[huh,wahy,uhn]",
        "HN"
    ],
    "hawk": [
        "['hawk']",
        "HK"
    ],
    "hawking": [
        "[haw,king]",
        "HKNK"
    ],
    "hawks": [
        "['hawks']",
        "HKS"
    ],
    "hay": [
        "[hey]",
        "H"
    ],
    "hazard": [
        "[haz,erd]",
        "HSRT"
    ],
    "haze": [
        "['heyz']",
        "HS"
    ],
    "hazy": [
        "['hey', 'zee']",
        "HS"
    ],
    "he": [
        "['hee']",
        "H"
    ],
    "he'll": [
        "['heel']",
        "HHL"
    ],
    "he's": [
        "['heez']",
        "HH"
    ],
    "head": [
        "['hed']",
        "HT"
    ],
    "head's": [
        "[hed,'s]",
        "HTTS"
    ],
    "headache": [
        "[hed,eyk]",
        "HTX"
    ],
    "headaches": [
        "[hed,eyk,s]",
        "HTXS"
    ],
    "headband": [
        "['hed', 'band']",
        "HTPNT"
    ],
    "headboard": [
        "['hed', 'bawrd']",
        "HTPRT"
    ],
    "headed": [
        "['hed', 'id']",
        "HTT"
    ],
    "heading": [
        "['hed', 'ing']",
        "HTNK"
    ],
    "headless": [
        "['hed', 'lis']",
        "HTLS"
    ],
    "headlights": [
        "['hed', 'lahyt', 's']",
        "HTLTS"
    ],
    "headline": [
        "[hed,lahyn]",
        "HTLN"
    ],
    "headliner": [
        "['hed', 'lahy', 'ner']",
        "HTLNR"
    ],
    "headlock": [
        "['hed', 'lok']",
        "HTLK"
    ],
    "headphones": [
        "[hed,fohn,s]",
        "HTFNS"
    ],
    "headquarters": [
        "[hed,kwawr,terz]",
        "HTKRTRS"
    ],
    "headrest": [
        "[hed,rest]",
        "HTRST"
    ],
    "heads": [
        "['hedz']",
        "HTS"
    ],
    "headshot": [
        "['hed', 'shot']",
        "HTXT"
    ],
    "headshots": [
        "[hed,shot,s]",
        "HTXTS"
    ],
    "heal": [
        "['heel']",
        "HL"
    ],
    "healed": [
        "['heel', 'ed']",
        "HLT"
    ],
    "healing": [
        "[hee,ling]",
        "HLNK"
    ],
    "heals": [
        "[heel,s]",
        "HLS"
    ],
    "health": [
        "['helth']",
        "HL0"
    ],
    "healthy": [
        "[hel,thee]",
        "HL0"
    ],
    "hear": [
        "['heer']",
        "HR"
    ],
    "heard": [
        "['heer', 'd']",
        "HRT"
    ],
    "hearing": [
        "['heer', 'ing']",
        "HRNK"
    ],
    "hears": [
        "[heer,s]",
        "HRS"
    ],
    "hearse": [
        "['hurs']",
        "HRS"
    ],
    "hearses": [
        "[hurs,s]",
        "HRSS"
    ],
    "heart": [
        "['hahrt']",
        "HRT"
    ],
    "heart's": [
        "['hahrt', \"'s\"]",
        "HRTTS"
    ],
    "heartbeat": [
        "['hahrt', 'beet']",
        "HRTPT"
    ],
    "heartbeats": [
        "[hahrt,beet,s]",
        "HRTPTS"
    ],
    "heartbreak": [
        "['hahrt', 'breyk']",
        "HRTPRK"
    ],
    "heartbreaker": [
        "['hahrt', 'brey', 'ker']",
        "HRTPRKR"
    ],
    "heartbroken": [
        "[hahrt,broh,kuhn]",
        "HRTPRKN"
    ],
    "heartless": [
        "['hahrt', 'lis']",
        "HRTLS"
    ],
    "hearts": [
        "['hahrt', 's']",
        "HRTS"
    ],
    "heartthrob": [
        "[hahrt,throb]",
        "HR0RP"
    ],
    "heat": [
        "['heet']",
        "HT"
    ],
    "heated": [
        "[hee,tid]",
        "HTT"
    ],
    "heater": [
        "['hee', 'ter']",
        "HTR"
    ],
    "heaters": [
        "['hee', 'ter', 's']",
        "HTRS"
    ],
    "heath": [
        "[heeth]",
        "H0"
    ],
    "heathen": [
        "['hee', 'thuhn']",
        "H0N"
    ],
    "heating": [
        "['heet', 'ing']",
        "HTNK"
    ],
    "heats": [
        "[heet,s]",
        "HTS"
    ],
    "heaven": [
        "['hev', 'uhn']",
        "HFN"
    ],
    "heaven's": [
        "['hev', 'uhn', \"'s\"]",
        "HFNNS"
    ],
    "heavenly": [
        "[hev,uhn,lee]",
        "HFNL"
    ],
    "heavens": [
        "[hev,uhn,s]",
        "HFNS"
    ],
    "heavily": [
        "['hev', 'uh', 'lee']",
        "HFL"
    ],
    "heavy": [
        "['hev', 'ee']",
        "HF"
    ],
    "heavyweight": [
        "['hev', 'ee', 'weyt']",
        "HFT"
    ],
    "heckler": [
        "[hek,uhl,r]",
        "HKLR"
    ],
    "hectic": [
        "['hek', 'tik']",
        "HKTK"
    ],
    "hector": [
        "['hek', 'ter']",
        "HKTR"
    ],
    "heed": [
        "['heed']",
        "HT"
    ],
    "heel": [
        "['heel']",
        "HL"
    ],
    "heels": [
        "['heel', 's']",
        "HLS"
    ],
    "hefner": [
        [
            "hef",
            "ner"
        ],
        "HFNR"
    ],
    "hefty": [
        "[hef,tee]",
        "HFT"
    ],
    "heh": [
        "['hey']",
        "H"
    ],
    "height": [
        "[hahyt]",
        "HT"
    ],
    "heights": [
        "['hahyt', 's']",
        "HTS"
    ],
    "heir": [
        "['air']",
        "HR"
    ],
    "heist": [
        "[hahyst]",
        "HST"
    ],
    "held": [
        "['held']",
        "HLT"
    ],
    "helicopter": [
        "['hel', 'i', 'kop', 'ter']",
        "HLKPTR"
    ],
    "helicopters": [
        "['hel', 'i', 'kop', 'ter', 's']",
        "HLKPTRS"
    ],
    "helipad": [
        "['hel', 'uh', 'pad']",
        "HLPT"
    ],
    "hell": [
        "['hel']",
        "HL"
    ],
    "hellcat": [
        "['hel', 'kat']",
        "HLKT"
    ],
    "heller": [
        "['hel', 'er']",
        "HLR"
    ],
    "hello": [
        "['he', 'loh']",
        "HL"
    ],
    "hells": [
        "[hel,s]",
        "HLS"
    ],
    "helluva": [
        "['hel', 'uh', 'vuh']",
        "HLF"
    ],
    "helmet": [
        "[hel,mit]",
        "HLMT"
    ],
    "help": [
        "['help']",
        "HLP"
    ],
    "helped": [
        "['help', 'ed']",
        "HLPT"
    ],
    "helping": [
        "['hel', 'ping']",
        "HLPNK"
    ],
    "helpless": [
        "[help,lis]",
        "HLPLS"
    ],
    "helps": [
        "[help,s]",
        "HLPS"
    ],
    "hem": [
        "[hem]",
        "HM"
    ],
    "hen": [
        "['hen']",
        "HN"
    ],
    "henchmen": [
        [
            "hench",
            "men"
        ],
        "HNXMN"
    ],
    "hendrix": [
        "['hen', 'driks']",
        "HNTRKS"
    ],
    "henny": [
        [
            "hen",
            "ee"
        ],
        "HN"
    ],
    "henry": [
        "[hen,ree]",
        "HNR"
    ],
    "her": [
        "['hur']",
        "HR"
    ],
    "herb": [
        "['urbor']",
        "HRP"
    ],
    "herbal": [
        "['ur', 'buhl']",
        "HRPL"
    ],
    "herbs": [
        "[urbor,s]",
        "HRPS"
    ],
    "hercules": [
        "['hur', 'kyuh', 'leez']",
        "HRKLS"
    ],
    "herd": [
        "[hurd]",
        "HRT"
    ],
    "here": [
        "['heer']",
        "HR"
    ],
    "here's": [
        "['heerz']",
        "HRS"
    ],
    "hereditary": [
        "['huh', 'red', 'i', 'ter', 'ee']",
        "HRTTR"
    ],
    "heres": [
        "['heer', 'eez']",
        "HRS"
    ],
    "hermes": [
        "['hur', 'meez']",
        "HRMS"
    ],
    "hero": [
        "['heer', 'oh']",
        "HR"
    ],
    "heroes": [
        "['heer', 'oh', 'es']",
        "HRS"
    ],
    "heroic": [
        "[hi,roh,ik]",
        "HRK"
    ],
    "heroin": [
        "['her', 'oh', 'in']",
        "HRN"
    ],
    "heron": [
        "[her,uhn]",
        "HRN"
    ],
    "herr": [
        "['her']",
        "HR"
    ],
    "herringbone": [
        "[her,ing,bohn]",
        "HRNKPN"
    ],
    "hers": [
        "['hurz']",
        "HRS"
    ],
    "herself": [
        "['her', 'self']",
        "HRSLF"
    ],
    "hershey": [
        "[hur,shee]",
        "HRX"
    ],
    "hes": [
        "['hee', 's']",
        "HS"
    ],
    "hesitant": [
        "[hez,i,tuhnt]",
        "HSTNT"
    ],
    "hesitate": [
        "['hez', 'i', 'teyt']",
        "HSTT"
    ],
    "hesitated": [
        "[hez,i,teyt,d]",
        "HSTTT"
    ],
    "hesitation": [
        "['hez', 'i', 'tey', 'shuhn']",
        "HSTXN"
    ],
    "hex": [
        "[heks]",
        "HKS"
    ],
    "hey": [
        "['hey']",
        "H"
    ],
    "hi": [
        "['hahy']",
        "H"
    ],
    "hiatus": [
        "[hahy,ey,tuhs]",
        "HTS"
    ],
    "hibachi": [
        "['hi', 'bah', 'chee']",
        "HPX"
    ],
    "hiccups": [
        "['hik', 'uhp', 's']",
        "HKPS"
    ],
    "hid": [
        "['hid']",
        "HT"
    ],
    "hidden": [
        "['hid', 'n']",
        "HTN"
    ],
    "hide": [
        "['hahyd']",
        "HT"
    ],
    "hideout": [
        "['hahyd', 'out']",
        "HTT"
    ],
    "hides": [
        "[hahyd,s]",
        "HTS"
    ],
    "hiding": [
        "['hahy', 'ding']",
        "HTNK"
    ],
    "high": [
        "['hahy']",
        "HH"
    ],
    "high's": [
        "['hahy', \"'s\"]",
        "HHH"
    ],
    "higher": [
        "['hahy', 'er']",
        "HHR"
    ],
    "highest": [
        "[hahy,est]",
        "HHST"
    ],
    "highlight": [
        "['hahy', 'lahyt']",
        "HHLT"
    ],
    "highlight's": [
        "[hahy,lahyt,'s]",
        "HHLTTS"
    ],
    "highlights": [
        "[hahy,lahyt,s]",
        "HHLTS"
    ],
    "highly": [
        "[hahy,lee]",
        "HHL"
    ],
    "highness": [
        "['hahy', 'nis']",
        "HHNS"
    ],
    "highs": [
        "[hahy,s]",
        "HHS"
    ],
    "highway": [
        "['hahy', 'wey']",
        "HH"
    ],
    "highways": [
        "[hahy,wey,s]",
        "HHS"
    ],
    "hijack": [
        "[hahy,jak]",
        "HJK"
    ],
    "hike": [
        "['hahyk']",
        "HK"
    ],
    "hilarious": [
        "[hi,lair,ee,uhs]",
        "HLRS"
    ],
    "hill": [
        "['hil']",
        "HL"
    ],
    "hillary": [
        "['hil', 'uh', 'ree']",
        "HLR"
    ],
    "hills": [
        "['hil', 's']",
        "HLS"
    ],
    "hilton": [
        "['hil', 'tn']",
        "HLTN"
    ],
    "him": [
        "['him']",
        "HM"
    ],
    "himself": [
        "['him', 'self']",
        "HMSLF"
    ],
    "hind": [
        "[hahynd]",
        "HNT"
    ],
    "hinges": [
        "['hinj', 's']",
        "HNJS"
    ],
    "hint": [
        "['hint']",
        "HNT"
    ],
    "hip": [
        "['hip']",
        "HP"
    ],
    "hippie": [
        "[hip,ee]",
        "HP"
    ],
    "hippy": [
        "[hip,ee]",
        "HP"
    ],
    "hips": [
        "['hip', 's']",
        "HPS"
    ],
    "hipster": [
        "[hip,ster]",
        "HPSTR"
    ],
    "hipsters": [
        "[hip,ster,s]",
        "HPSTRS"
    ],
    "hire": [
        "['hahyuhr']",
        "HR"
    ],
    "hired": [
        "['hahyuhr', 'd']",
        "HRT"
    ],
    "his": [
        "['hiz']",
        "HS"
    ],
    "history": [
        "['his', 'tuh', 'ree']",
        "HSTR"
    ],
    "hit": [
        "['hit']",
        "HT"
    ],
    "hitched": [
        "[hich,ed]",
        "HXT"
    ],
    "hitchhiker": [
        "[hich,hahyk,r]",
        "HXKR"
    ],
    "hitler": [
        "['hit', 'ler']",
        "HTLR"
    ],
    "hits": [
        "['hit', 's']",
        "HTS"
    ],
    "hitter": [
        "['hit', 'ter']",
        "HTR"
    ],
    "hitters": [
        "['hit', 'ters']",
        "HTRS"
    ],
    "hitting": [
        "['hit', 'ting']",
        "HTNK"
    ],
    "hiv": [
        "[(ch,v)]",
        "HF"
    ],
    "hive": [
        "[hahyv]",
        "HF"
    ],
    "hm": [
        "['hmm']",
        "M"
    ],
    "ho": [
        "['hoh']",
        "H"
    ],
    "ho's": [
        "['hoh', \"'s\"]",
        "HH"
    ],
    "hoarse": [
        "['hawrs']",
        "HRS"
    ],
    "hobby": [
        "['hob', 'ee']",
        "HP"
    ],
    "hobo": [
        "[hoh,boh]",
        "HP"
    ],
    "hockey": [
        "['hok', 'ee']",
        "HK"
    ],
    "hocks": [
        "[hok,s]",
        "HKS"
    ],
    "hocus": [
        "['hoh', 'kuhs']",
        "HKS"
    ],
    "hoe": [
        "['hoh']",
        "H"
    ],
    "hoe'ing": [
        [
            "hoh",
            "ing"
        ],
        "HNK"
    ],
    "hoe's": [
        "['hoh', \"'s\"]",
        "HS"
    ],
    "hoeing": [
        "['hoh', 'ing']",
        "HNK"
    ],
    "hoes": [
        "['hoh', 's']",
        "HS"
    ],
    "hoffa": [
        "[hof,uh]",
        "HF"
    ],
    "hog": [
        "['hawg']",
        "HK"
    ],
    "hogan": [
        "['hoh', 'gawn']",
        "HKN"
    ],
    "hogging": [
        "['hawg', 'ging']",
        "HJNK"
    ],
    "hold": [
        "['hohld']",
        "HLT"
    ],
    "holder": [
        "[hohl,der]",
        "HLTR"
    ],
    "holding": [
        "['hohl', 'ding']",
        "HLTNK"
    ],
    "holds": [
        "['hohld', 's']",
        "HLTS"
    ],
    "hole": [
        "['hohl']",
        "HL"
    ],
    "holes": [
        "['hohl', 's']",
        "HLS"
    ],
    "holiday": [
        "['hol', 'i', 'dey']",
        "HLT"
    ],
    "holidays": [
        "[hol,i,dey,s]",
        "HLTS"
    ],
    "holland": [
        "[hol,uhnd]",
        "HLNT"
    ],
    "holler": [
        "['hol', 'er']",
        "HLR"
    ],
    "hollered": [
        "[hol,er,ed]",
        "HLRT"
    ],
    "hollering": [
        "['hol', 'er', 'ing']",
        "HLRNK"
    ],
    "hollow": [
        "['hol', 'oh']",
        "HL"
    ],
    "hollows": [
        "[hol,oh,s]",
        "HLS"
    ],
    "holly": [
        "[hol,ee]",
        "HL"
    ],
    "hollywood": [
        "['hol', 'ee', 'wood']",
        "HLT"
    ],
    "holmes": [
        "['hohmz']",
        "HLMS"
    ],
    "holocaust": [
        "['hol', 'uh', 'kawst']",
        "HLKST"
    ],
    "holster": [
        "['hohl', 'ster']",
        "HLSTR"
    ],
    "holy": [
        "['hoh', 'lee']",
        "HL"
    ],
    "homage": [
        "['hom', 'ij']",
        "HMJ"
    ],
    "home": [
        "['hohm']",
        "HM"
    ],
    "homeboy": [
        "['hohm', 'boi']",
        "HMP"
    ],
    "homeboy's": [
        "[hohm,boi,'s]",
        "HMPS"
    ],
    "homeboys": [
        "['hohm', 'boi', 's']",
        "HMPS"
    ],
    "homecoming": [
        "[hohm,kuhm,ing]",
        "HMKMNK"
    ],
    "homegirl": [
        "[hohm,gurl]",
        "HMJRL"
    ],
    "homegirls": [
        "['hohm', 'gurl', 's']",
        "HMJRLS"
    ],
    "homegrown": [
        "[hohm,grohn]",
        "HMKRN"
    ],
    "homeless": [
        "['hohm', 'lis']",
        "HMLS"
    ],
    "homer": [
        "[hoh,mer]",
        "HMR"
    ],
    "homes": [
        "['hohm', 's']",
        "HMS"
    ],
    "hometown": [
        "[hohm,toun]",
        "HMTN"
    ],
    "homework": [
        "['hohm', 'wurk']",
        "HMRK"
    ],
    "homey": [
        "['hoh', 'mee']",
        "HM"
    ],
    "homicide": [
        "['hom', 'uh', 'sahyd']",
        "HMST"
    ],
    "homicides": [
        "[hom,uh,sahyd,s]",
        "HMSTS"
    ],
    "homie": [
        "['hoh', 'mee']",
        "HM"
    ],
    "homies": [
        "['hoh', 'mee', 's']",
        "HMS"
    ],
    "homo": [
        "['hoh', 'moh']",
        "HM"
    ],
    "homos": [
        "[hoh,moh,s]",
        "HMS"
    ],
    "honda": [
        "['hon', 'duh']",
        "HNT"
    ],
    "honest": [
        "['on', 'ist']",
        "HNST"
    ],
    "honestly": [
        "['on', 'ist', 'lee']",
        "HNSTL"
    ],
    "honesty": [
        "[on,uh,stee]",
        "HNST"
    ],
    "honey": [
        "['huhn', 'ee']",
        "HN"
    ],
    "honey's": [
        "[huhn,ee,'s]",
        "HNS"
    ],
    "honeymoon": [
        "['huhn', 'ee', 'moon']",
        "HNMN"
    ],
    "honeys": [
        "[huhn,ee,s]",
        "HNS"
    ],
    "honk": [
        "[hongk]",
        "HNK"
    ],
    "honor": [
        "['on', 'er']",
        "HNR"
    ],
    "honored": [
        "[on,erd]",
        "HNRT"
    ],
    "honors": [
        "[on,er,s]",
        "HNRS"
    ],
    "hooch": [
        "['hooch']",
        "HX"
    ],
    "hood": [
        "['hood']",
        "HT"
    ],
    "hoodie": [
        "['hood', 'ee']",
        "HT"
    ],
    "hoods": [
        "['hood', 's']",
        "HTS"
    ],
    "hook": [
        "['hook']",
        "HK"
    ],
    "hookah": [
        "['hook', 'uh']",
        "HK"
    ],
    "hooked": [
        "['hookt']",
        "HKT"
    ],
    "hooker": [
        "['hook', 'er']",
        "HKR"
    ],
    "hookers": [
        "['hook', 'er', 's']",
        "HKRS"
    ],
    "hooks": [
        "[hooks]",
        "HKS"
    ],
    "hooligan": [
        "[hoo,li,guhn]",
        "HLKN"
    ],
    "hooligans": [
        "[hoo,li,guhn,s]",
        "HLKNS"
    ],
    "hoop": [
        "['hoop']",
        "HP"
    ],
    "hooping": [
        "['hoop', 'ing']",
        "HPNK"
    ],
    "hoops": [
        "[hoop,s]",
        "HPS"
    ],
    "hooray": [
        "[hoo,rey]",
        "HR"
    ],
    "hoot": [
        "[hoot]",
        "HT"
    ],
    "hooter": [
        "[hoo,ter]",
        "HTR"
    ],
    "hooters": [
        "['hoo', 'ter', 's']",
        "HTRS"
    ],
    "hoover": [
        "[hoo,ver]",
        "HFR"
    ],
    "hop": [
        "['hop']",
        "HP"
    ],
    "hope": [
        "['hohp']",
        "HP"
    ],
    "hoped": [
        "[hohp,d]",
        "HPT"
    ],
    "hopefully": [
        "[hohp,fuh,lee]",
        "HPFL"
    ],
    "hopeless": [
        "['hohp', 'lis']",
        "HPLS"
    ],
    "hopes": [
        "[hohp,s]",
        "HPS"
    ],
    "hopped": [
        "['hop', 'ped']",
        "HPT"
    ],
    "hopping": [
        "['hop', 'ing']",
        "HPNK"
    ],
    "hops": [
        "[hop,s]",
        "HPS"
    ],
    "hopscotch": [
        "['hop', 'skoch']",
        "HPSKX"
    ],
    "horizon": [
        "[huh,rahy,zuhn]",
        "HRSN"
    ],
    "horizontal": [
        "[hawr,uh,zon,tl]",
        "HRSNTL"
    ],
    "hormones": [
        "[hawr,mohn,s]",
        "HRMNS"
    ],
    "horn": [
        "[hawrn]",
        "HRN"
    ],
    "hornet": [
        "[hawr,nit]",
        "HRNT"
    ],
    "hornets": [
        "['hawr', 'nit', 's']",
        "HRNTS"
    ],
    "horns": [
        "['hawrn', 's']",
        "HRNS"
    ],
    "horny": [
        "['hawr', 'nee']",
        "HRN"
    ],
    "horoscope": [
        "[hawr,uh,skohp]",
        "HRSKP"
    ],
    "horrible": [
        "[hawr,uh,buhl]",
        "HRPL"
    ],
    "horror": [
        "[hawr,er]",
        "HRR"
    ],
    "horse": [
        "['hawrs']",
        "HRS"
    ],
    "horses": [
        "['hawrs', 's']",
        "HRSS"
    ],
    "hos": [
        "['hoh', 's']",
        "HS"
    ],
    "hose": [
        "[hohz]",
        "HS"
    ],
    "hospital": [
        "['hos', 'pi', 'tl']",
        "HSPTL"
    ],
    "hospitality": [
        "[hos,pi,tal,i,tee]",
        "HSPTLT"
    ],
    "host": [
        "[hohst]",
        "HST"
    ],
    "hostage": [
        "['hos', 'tij']",
        "HSTJ"
    ],
    "hostages": [
        "[hos,tij,s]",
        "HSTJS"
    ],
    "hostile": [
        "[hos,tlor]",
        "HSTL"
    ],
    "hosting": [
        "['hohst', 'ing']",
        "HSTNK"
    ],
    "hot": [
        "['hot']",
        "HT"
    ],
    "hotbox": [
        "['hot', 'boks']",
        "HTPKS"
    ],
    "hotel": [
        "['hoh', 'tel']",
        "HTL"
    ],
    "hotels": [
        "[hoh,tel,s]",
        "HTLS"
    ],
    "hotter": [
        "['hot', 'er']",
        "HTR"
    ],
    "hottest": [
        "['hot', 'test']",
        "HTST"
    ],
    "hotties": [
        "['hot', 'ee', 's']",
        "HTS"
    ],
    "houdini": [
        "['hoo', 'dee', 'nee']",
        "HTN"
    ],
    "hound": [
        "['hound']",
        "HNT"
    ],
    "hour": [
        "['ouuhr']",
        "HR"
    ],
    "hours": [
        "['ouuhr', 's']",
        "HRS"
    ],
    "house": [
        "['noun']",
        "HS"
    ],
    "house's": [
        "['noun', \"'s\"]",
        "HSS"
    ],
    "household": [
        "[hous,hohld]",
        "HSHLT"
    ],
    "housekeeper": [
        "[hous,kee,per]",
        "HSKPR"
    ],
    "housekeeping": [
        "[hous,kee,ping]",
        "HSKPNK"
    ],
    "houses": [
        "['noun', 's']",
        "HSS"
    ],
    "housewife": [
        "['hous', 'wahyfor']",
        "HSF"
    ],
    "housewives": [
        [
            "hous",
            "wahyvz"
        ],
        "HSFS"
    ],
    "housing": [
        "['hou', 'zing']",
        "HSNK"
    ],
    "houston": [
        "['hyoo', 'stuhn']",
        "HSTN"
    ],
    "hove": [
        "[hohv]",
        "HF"
    ],
    "hover": [
        "[huhv,er]",
        "HFR"
    ],
    "how": [
        "['hou']",
        "H"
    ],
    "howard": [
        "[hou,erd]",
        "HRT"
    ],
    "howdy": [
        "[hou,dee]",
        "HT"
    ],
    "however": [
        "['hou', 'ev', 'er']",
        "HFR"
    ],
    "howl": [
        "['houl']",
        "HL"
    ],
    "hoya": [
        "[hoi,uh]",
        "H"
    ],
    "hubby": [
        "[huhb,ee]",
        "HP"
    ],
    "hublot": [
        [
            "huhb",
            "lot"
        ],
        "HPLT"
    ],
    "hubris": [
        "[hyoo,bris]",
        "HPRS"
    ],
    "huddle": [
        "['huhd', 'l']",
        "HTL"
    ],
    "huffy": [
        "['huhf', 'ee']",
        "HF"
    ],
    "hug": [
        "['huhg']",
        "HK"
    ],
    "huge": [
        "[hyoojor]",
        "HJ"
    ],
    "hugged": [
        "[huhg,ged]",
        "HKT"
    ],
    "hugging": [
        "[huhg,ging]",
        "HKNK"
    ],
    "hugh": [
        "['hyooor']",
        "HH"
    ],
    "hugo": [
        "[hyoo,gohor]",
        "HK"
    ],
    "hugs": [
        "['huhg', 's']",
        "HKS"
    ],
    "huh": [
        "['huh']",
        "H"
    ],
    "hula": [
        "['hoo', 'luh']",
        "HL"
    ],
    "hulk": [
        "['huhlk']",
        "HLK"
    ],
    "hum": [
        "['huhm']",
        "HM"
    ],
    "human": [
        "['hyoo', 'muhnor']",
        "HMN"
    ],
    "humanity": [
        "['hyoo', 'man', 'i', 'teeor']",
        "HMNT"
    ],
    "humans": [
        "[hyoo,muhnor,s]",
        "HMNS"
    ],
    "humble": [
        "['huhm', 'buhl']",
        "HMPL"
    ],
    "hummer": [
        "['huhm', 'er']",
        "HMR"
    ],
    "hummers": [
        "['huhm', 'er', 's']",
        "HMRS"
    ],
    "humongous": [
        "[hyoo,muhng,guhs]",
        "HMNKS"
    ],
    "humor": [
        "[hyoo,meror]",
        "HMR"
    ],
    "hump": [
        "['huhmp']",
        "HMP"
    ],
    "humped": [
        "[huhmpt]",
        "HMPT"
    ],
    "humping": [
        "[huhmp,ing]",
        "HMPNK"
    ],
    "humvee": [
        "['huhm', 'vee']",
        "HMF"
    ],
    "hun": [
        "['huhn']",
        "HN"
    ],
    "hunchback": [
        "[huhnch,bak]",
        "HNXPK"
    ],
    "hundred": [
        "['huhn', 'drid']",
        "HNTRT"
    ],
    "hundreds": [
        "['huhn', 'drid', 's']",
        "HNTRTS"
    ],
    "hung": [
        "['huhng']",
        "HNK"
    ],
    "hunger": [
        "['huhng', 'ger']",
        "HNKR"
    ],
    "hungry": [
        "['huhng', 'gree']",
        "HNKR"
    ],
    "hunt": [
        "['huhnt']",
        "HNT"
    ],
    "hunter": [
        "['huhn', 'ter']",
        "HNTR"
    ],
    "hunters": [
        "['huhn', 'ter', 's']",
        "HNTRS"
    ],
    "hunting": [
        "['huhn', 'ting']",
        "HNTNK"
    ],
    "hurdle": [
        "['hur', 'dl']",
        "HRTL"
    ],
    "hurl": [
        "['hurl']",
        "HRL"
    ],
    "hurled": [
        "[hurl,ed]",
        "HRLT"
    ],
    "hurricane": [
        "['hur', 'i', 'keyn']",
        "HRKN"
    ],
    "hurricanes": [
        "[hur,i,keyn,s]",
        "HRKNS"
    ],
    "hurry": [
        "['hur', 'ee']",
        "HR"
    ],
    "hurt": [
        "['hurt']",
        "HRT"
    ],
    "hurting": [
        "['hurt', 'ing']",
        "HRTNK"
    ],
    "hurts": [
        "['hurt', 's']",
        "HRTS"
    ],
    "husband": [
        "['huhz', 'buhnd']",
        "HSPNT"
    ],
    "hush": [
        "[huhsh]",
        "HX"
    ],
    "husky": [
        "[huhs,kee]",
        "HSK"
    ],
    "hussein": [
        "['hoo', 'seyn']",
        "HSN"
    ],
    "hustle": [
        "['huhs', 'uhl']",
        "HSTL"
    ],
    "hustle's": [
        "[huhs,uhl,'s]",
        "HSTLS"
    ],
    "hustled": [
        "[huhs,uhl,d]",
        "HSTLT"
    ],
    "hustler": [
        "['huhs', 'ler']",
        "HSTLR"
    ],
    "hustler's": [
        "[huhs,ler,'s]",
        "HSTLRRS"
    ],
    "hustlers": [
        "['huhs', 'ler', 's']",
        "HSTLRS"
    ],
    "hut": [
        "['huht']",
        "HT"
    ],
    "hydrant": [
        "[hahy,druhnt]",
        "HTRNT"
    ],
    "hydro": [
        "['hahy', 'droh']",
        "HTR"
    ],
    "hydroplane": [
        "[hahy,druh,pleyn]",
        "HTRPLN"
    ],
    "hyenas": [
        "['hahy', 'ee', 'nuh', 's']",
        "HNS"
    ],
    "hype": [
        "['hahyp']",
        "HP"
    ],
    "hyped": [
        "[hahyp,d]",
        "HPT"
    ],
    "hyperventilate": [
        "['hahy', 'per', 'ven', 'tl', 'eyt']",
        "HPRFNTLT"
    ],
    "hyphen": [
        "[hahy,fuhn]",
        "HFN"
    ],
    "hypnotic": [
        "['hip', 'not', 'ik']",
        "HPNTK"
    ],
    "hypnotized": [
        "['hip', 'nuh', 'tahyz', 'd']",
        "HPNTST"
    ],
    "hypocrite": [
        "[hip,uh,krit]",
        "HPKRT"
    ],
    "hysterical": [
        "[hi,ster,i,kuhl]",
        "HSTRKL"
    ],
    "i": [
        "['ahy', '']",
        "A"
    ],
    "i'd": [
        "['ahyd']",
        "AAT"
    ],
    "i'll": [
        "['ahyl']",
        "AAL"
    ],
    "i've": [
        "['ahyv']",
        "AAF"
    ],
    "ibiza": [
        "['ee', 'vee', 'thah']",
        "APS"
    ],
    "ice": [
        "['ahys']",
        "AS"
    ],
    "iceberg": [
        "['ahys', 'burg']",
        "ASPRK"
    ],
    "iced": [
        "['ahyst']",
        "AST"
    ],
    "iceland": [
        "['ahys', 'luhnd']",
        "ASLNT"
    ],
    "icicle": [
        "[ahy,si,kuhl]",
        "ASKL"
    ],
    "icicles": [
        "[ahy,si,kuhl,s]",
        "ASKLS"
    ],
    "icing": [
        "['ahy', 'sing']",
        "ASNK"
    ],
    "icky": [
        "['ik', 'ee']",
        "AK"
    ],
    "icon": [
        "['ahy', 'kon']",
        "AKN"
    ],
    "icons": [
        "[ahy,kon,s]",
        "AKNS"
    ],
    "icy": [
        "['ahy', 'see']",
        "AS"
    ],
    "id": [
        "['id']",
        "AT"
    ],
    "idea": [
        "['ahy', 'dee', 'uh']",
        "AT"
    ],
    "ideas": [
        "['ahy', 'dee', 'uh', 's']",
        "ATS"
    ],
    "identical": [
        "['ahy', 'den', 'ti', 'kuhl']",
        "ATNTKL"
    ],
    "identify": [
        "['ahy', 'den', 'tuh', 'fahy']",
        "ATNTF"
    ],
    "identity": [
        "['ahy', 'den', 'ti', 'tee']",
        "ATNTT"
    ],
    "idiot": [
        "['id', 'ee', 'uht']",
        "ATT"
    ],
    "idle": [
        "[ahyd,l]",
        "ATL"
    ],
    "idol": [
        "['ahyd', 'l']",
        "ATL"
    ],
    "idols": [
        "[ahyd,l,s]",
        "ATLS"
    ],
    "if": [
        "['if']",
        "AF"
    ],
    "iffy": [
        "[if,ee]",
        "AF"
    ],
    "igloo": [
        "['ig', 'loo']",
        "AKL"
    ],
    "ignite": [
        "['ig', 'nahyt']",
        "AKNT"
    ],
    "ignited": [
        "['ig', 'nahyt', 'd']",
        "AKNTT"
    ],
    "ignition": [
        "[ig,nish,uhn]",
        "AKNXN"
    ],
    "ignorance": [
        "[ig,ner,uhns]",
        "AKNRNS"
    ],
    "ignorant": [
        "['ig', 'ner', 'uhnt']",
        "AKNRNT"
    ],
    "ignore": [
        "['ig', 'nawr']",
        "AKNR"
    ],
    "ignored": [
        "['ig', 'nawr', 'd']",
        "AKNRT"
    ],
    "ii": [
        [
            "ahy",
            "ahy"
        ],
        "A"
    ],
    "ike": [
        "['ahyk']",
        "AK"
    ],
    "ill": [
        "['il']",
        "AL"
    ],
    "illegal": [
        "['ih', 'lee', 'guhl']",
        "ALKL"
    ],
    "iller": [
        "[il,er]",
        "ALR"
    ],
    "illest": [
        "['il', 'est']",
        "ALST"
    ],
    "illinois": [
        "[il,uh,noior]",
        "ALN"
    ],
    "illiterate": [
        "[ih,lit,er,it]",
        "ALTRT"
    ],
    "ills": [
        "['il', 's']",
        "ALS"
    ],
    "illuminate": [
        "[verbih,loo,muh,neyt]",
        "ALMNT"
    ],
    "illuminati": [
        "['ih', 'loo', 'muh', 'nah', 'tee']",
        "ALMNT"
    ],
    "illusion": [
        "[ih,loo,zhuhn]",
        "ALSN"
    ],
    "image": [
        "['im', 'ij']",
        "AMJ"
    ],
    "images": [
        "[im,ij,s]",
        "AMJS"
    ],
    "imaginary": [
        "[ih,maj,uh,ner,ee]",
        "AMJNR"
    ],
    "imagination": [
        "['ih', 'maj', 'uh', 'ney', 'shuhn']",
        "AMJNXN"
    ],
    "imagine": [
        "['ih', 'maj', 'in']",
        "AMJN"
    ],
    "imagined": [
        "['ih', 'maj', 'in', 'd']",
        "AMJNT"
    ],
    "imitate": [
        "[im,i,teyt]",
        "AMTT"
    ],
    "imitation": [
        "[im,i,tey,shuhn]",
        "AMTXN"
    ],
    "imitations": [
        "[im,i,tey,shuhn,s]",
        "AMTXNS"
    ],
    "immaculate": [
        "['ih', 'mak', 'yuh', 'lit']",
        "AMKLT"
    ],
    "immature": [
        "['im', 'uh', 'choor']",
        "AMTR"
    ],
    "immigrant": [
        "['im', 'i', 'gruhnt']",
        "AMKRNT"
    ],
    "immigrants": [
        "[im,i,gruhnt,s]",
        "AMKRNTS"
    ],
    "immigration": [
        "['im', 'i', 'grey', 'shuhn']",
        "AMKRXN"
    ],
    "immortal": [
        "['ih', 'mawr', 'tl']",
        "AMRTL"
    ],
    "immune": [
        "['ih', 'myoon']",
        "AMN"
    ],
    "impact": [
        "[nounim,pakt]",
        "AMPKT"
    ],
    "impala": [
        "['im', 'pal', 'uh']",
        "AMPL"
    ],
    "impalas": [
        "['im', 'pal', 'uh', 's']",
        "AMPLS"
    ],
    "impatient": [
        "['im', 'pey', 'shuhnt']",
        "AMPTNT"
    ],
    "impeccable": [
        "['im', 'pek', 'uh', 'buhl']",
        "AMPKPL"
    ],
    "imperial": [
        "['im', 'peer', 'ee', 'uhl']",
        "AMPRL"
    ],
    "import": [
        "['verbim', 'pawrt']",
        "AMPRT"
    ],
    "important": [
        "['im', 'pawr', 'tnt']",
        "AMPRTNT"
    ],
    "imported": [
        "[verbim,pawrt,ed]",
        "AMPRTT"
    ],
    "impossible": [
        "[im,pos,uh,buhl]",
        "AMPSPL"
    ],
    "impostors": [
        "[im,pos,ter,s]",
        "AMPSTRS"
    ],
    "impress": [
        "['verbim', 'pres']",
        "AMPRS"
    ],
    "impressed": [
        "['verbim', 'pres', 'ed']",
        "AMPRST"
    ],
    "impressing": [
        "[verbim,pres,ing]",
        "AMPRSNK"
    ],
    "impression": [
        "[im,presh,uhn]",
        "AMPRSN"
    ],
    "improve": [
        "['im', 'proov']",
        "AMPRF"
    ],
    "improved": [
        "[im,proov,d]",
        "AMPRFT"
    ],
    "improvement": [
        "['im', 'proov', 'muhnt']",
        "AMPRFMNT"
    ],
    "improvise": [
        "['im', 'pruh', 'vahyz']",
        "AMPRFS"
    ],
    "imus": [
        "[ee,moo,s]",
        "AMS"
    ],
    "in": [
        "['in']",
        "AN"
    ],
    "incase": [
        "['in', 'keys']",
        "ANKS"
    ],
    "incense": [
        "[in,sens]",
        "ANSNS"
    ],
    "incest": [
        "['in', 'sest']",
        "ANSST"
    ],
    "inch": [
        "['inch']",
        "ANX"
    ],
    "inches": [
        "['inch', 'es']",
        "ANXS"
    ],
    "incident": [
        "['in', 'si', 'duhnt']",
        "ANSTNT"
    ],
    "incidentals": [
        "['in', 'si', 'den', 'tl', 's']",
        "ANSTNTLS"
    ],
    "income": [
        "['in', 'kuhm']",
        "ANKM"
    ],
    "incomplete": [
        "['in', 'kuhm', 'pleet']",
        "ANKMPLT"
    ],
    "inconsiderate": [
        "[in,kuhn,sid,er,it]",
        "ANKNSTRT"
    ],
    "incorrect": [
        "[in,kuh,rekt]",
        "ANKRKT"
    ],
    "increase": [
        "['verbin', 'krees']",
        "ANKRS"
    ],
    "incredible": [
        "['in', 'kred', 'uh', 'buhl']",
        "ANKRTPL"
    ],
    "indecisive": [
        "[in,di,sahy,siv]",
        "ANTSSF"
    ],
    "indeed": [
        "['in', 'deed']",
        "ANTT"
    ],
    "independence": [
        "[in,di,pen,duhns]",
        "ANTPNTNS"
    ],
    "independent": [
        "['in', 'di', 'pen', 'duhnt']",
        "ANTPNTNT"
    ],
    "index": [
        "['in', 'deks']",
        "ANTKS"
    ],
    "india": [
        "[in,dee,uh]",
        "ANT"
    ],
    "indian": [
        "['in', 'dee', 'uhn']",
        "ANTN"
    ],
    "indians": [
        "[in,dee,uhn,s]",
        "ANTNS"
    ],
    "indicted": [
        "[in,dahyt,ed]",
        "ANTKTT"
    ],
    "indictments": [
        "['in', 'dahyt', 'muhnt', 's']",
        "ANTKTMNTS"
    ],
    "individual": [
        "[in,duh,vij,oo,uhl]",
        "ANTFTL"
    ],
    "individuals": [
        "[in,duh,vij,oo,uhl,s]",
        "ANTFTLS"
    ],
    "indoor": [
        "[in,dawr]",
        "ANTR"
    ],
    "industry": [
        "['in', 'duh', 'stree']",
        "ANTSTR"
    ],
    "industry's": [
        "[in,duh,stree,'s]",
        "ANTSTRS"
    ],
    "inevitable": [
        "[in,ev,i,tuh,buhl]",
        "ANFTPL"
    ],
    "infamous": [
        "[in,fuh,muhs]",
        "ANFMS"
    ],
    "infant": [
        "[in,fuhnt]",
        "ANFNT"
    ],
    "infatuated": [
        "['verbin', 'fach', 'oo', 'eyt', 'd']",
        "ANFTTT"
    ],
    "infatuation": [
        "['in', 'fach', 'oo', 'ey', 'shuhn']",
        "ANFTXN"
    ],
    "infected": [
        "['in', 'fekt', 'ed']",
        "ANFKTT"
    ],
    "infection": [
        "[in,fek,shuhn]",
        "ANFKXN"
    ],
    "inferior": [
        "[in,feer,ee,er]",
        "ANFRR"
    ],
    "inferno": [
        "[in,fur,noh]",
        "ANFRN"
    ],
    "infested": [
        "[in,fest,ed]",
        "ANFSTT"
    ],
    "infiltrated": [
        "[in,fil,treyt,d]",
        "ANFLTRTT"
    ],
    "infinite": [
        "[in,fuh,nit]",
        "ANFNT"
    ],
    "infinitely": [
        "[in,fuh,nit,ly]",
        "ANFNTL"
    ],
    "infinity": [
        "['in', 'fin', 'i', 'tee']",
        "ANFNT"
    ],
    "inflation": [
        "[in,fley,shuhn]",
        "ANFLXN"
    ],
    "influence": [
        "['in', 'floo', 'uhns']",
        "ANFLNS"
    ],
    "influenced": [
        "['in', 'floo', 'uhns', 'd']",
        "ANFLNST"
    ],
    "influential": [
        "[in,floo,en,shuhl]",
        "ANFLNXL"
    ],
    "info": [
        "[in,foh]",
        "ANF"
    ],
    "informants": [
        "[in,fawr,muhnt,s]",
        "ANFRMNTS"
    ],
    "information": [
        "['in', 'fer', 'mey', 'shuhn']",
        "ANFRMXN"
    ],
    "informed": [
        "[in,fawrmd]",
        "ANFRMT"
    ],
    "infrared": [
        "[in,fruh,red]",
        "ANFRRT"
    ],
    "inhale": [
        "[in,heyl]",
        "ANL"
    ],
    "inherit": [
        "[in,her,it]",
        "ANRT"
    ],
    "initial": [
        "[ih,nish,uhl]",
        "ANXL"
    ],
    "initials": [
        "[ih,nish,uhl,s]",
        "ANXLS"
    ],
    "inject": [
        "[in,jekt]",
        "ANJKT"
    ],
    "injection": [
        "[in,jek,shuhn]",
        "ANJKXN"
    ],
    "ink": [
        "['ingk']",
        "ANK"
    ],
    "inky": [
        "[ing,kee]",
        "ANK"
    ],
    "inn": [
        "[in]",
        "AN"
    ],
    "inner": [
        "['in', 'er']",
        "ANR"
    ],
    "inning": [
        "[in,ing]",
        "ANNK"
    ],
    "innocence": [
        "[in,uh,suhns]",
        "ANSNS"
    ],
    "innocent": [
        "['in', 'uh', 'suhnt']",
        "ANSNT"
    ],
    "innovative": [
        "[in,uh,vey,tiv]",
        "ANFTF"
    ],
    "insane": [
        "['in', 'seyn']",
        "ANSN"
    ],
    "insanity": [
        "[in,san,i,tee]",
        "ANSNT"
    ],
    "insecure": [
        "['in', 'si', 'kyoor']",
        "ANSKR"
    ],
    "insecurity": [
        "['in', 'si', 'kyoor', 'i', 'tee']",
        "ANSKRT"
    ],
    "insensitive": [
        "[in,sen,si,tiv]",
        "ANSNSTF"
    ],
    "inside": [
        "['prepositionin', 'sahyd']",
        "ANST"
    ],
    "inside's": [
        "[prepositionin,sahyd,'s]",
        "ANSTS"
    ],
    "insides": [
        "['prepositionin', 'sahyd', 's']",
        "ANSTS"
    ],
    "insight": [
        "[in,sahyt]",
        "ANST"
    ],
    "insist": [
        "[in,sist]",
        "ANSST"
    ],
    "insists": [
        "['in', 'sist', 's']",
        "ANSSTS"
    ],
    "insomniac": [
        "[in,som,nee,ak]",
        "ANSMNK"
    ],
    "inspector": [
        "[in,spek,ter]",
        "ANSPKTR"
    ],
    "inspiration": [
        "[in,spuh,rey,shuhn]",
        "ANSPRXN"
    ],
    "inspire": [
        "['in', 'spahyuhr']",
        "ANSPR"
    ],
    "inspired": [
        "[in,spahyuhrd]",
        "ANSPRT"
    ],
    "instagram": [
        "['in', 'stuh', 'gram']",
        "ANSTKRM"
    ],
    "instance": [
        "[in,stuhns]",
        "ANSTNS"
    ],
    "instant": [
        "['in', 'stuhnt']",
        "ANSTNT"
    ],
    "instantly": [
        "['in', 'stuhnt', 'lee']",
        "ANSTNTL"
    ],
    "instead": [
        "['in', 'sted']",
        "ANSTT"
    ],
    "instigated": [
        "['in', 'sti', 'geyt', 'd']",
        "ANSTKTT"
    ],
    "instinct": [
        "[in,stingkt]",
        "ANSTNKT"
    ],
    "instincts": [
        "[in,stingkt,s]",
        "ANSTNKTS"
    ],
    "institution": [
        "[in,sti,too,shuhn]",
        "ANSTTXN"
    ],
    "instrumental": [
        "['in', 'struh', 'men', 'tl']",
        "ANSTRMNTL"
    ],
    "instrumentals": [
        "['in', 'struh', 'men', 'tl', 's']",
        "ANSTRMNTLS"
    ],
    "insult": [
        "[verbin,suhlt]",
        "ANSLT"
    ],
    "insurance": [
        "['in', 'shoor', 'uhns']",
        "ANSRNS"
    ],
    "insured": [
        "[in,shoord]",
        "ANSRT"
    ],
    "intact": [
        "['in', 'takt']",
        "ANTKT"
    ],
    "integrity": [
        "['in', 'teg', 'ri', 'tee']",
        "ANTKRT"
    ],
    "intellect": [
        "[in,tl,ekt]",
        "ANTLKT"
    ],
    "intellectual": [
        "[in,tl,ek,choo,uhl]",
        "ANTLKTL"
    ],
    "intelligence": [
        "[in,tel,i,juhns]",
        "ANTLJNS"
    ],
    "intelligent": [
        "[in,tel,i,juhnt]",
        "ANTLJNT"
    ],
    "intend": [
        "[in,tend]",
        "ANTNT"
    ],
    "intended": [
        "[in,ten,did]",
        "ANTNTT"
    ],
    "intense": [
        "[in,tens]",
        "ANTNS"
    ],
    "intensive": [
        "[in,ten,siv]",
        "ANTNSF"
    ],
    "intention": [
        "[in,ten,shuhn]",
        "ANTNXN"
    ],
    "intentions": [
        "['in', 'ten', 'shuhn', 's']",
        "ANTNXNS"
    ],
    "intercept": [
        "['verbin', 'ter', 'sept']",
        "ANTRSPT"
    ],
    "interception": [
        "[in,ter,sep,shuhn]",
        "ANTRSPXN"
    ],
    "intercontinental": [
        "['in', 'ter', 'kon', 'tn', 'en', 'tl']",
        "ANTRKNTNNTL"
    ],
    "interest": [
        "['in', 'ter', 'ist']",
        "ANTRST"
    ],
    "interesting": [
        "[in,ter,uh,sting]",
        "ANTRSTNK"
    ],
    "interfere": [
        "[in,ter,feer]",
        "ANTRFR"
    ],
    "interior": [
        "['in', 'teer', 'ee', 'er']",
        "ANTRR"
    ],
    "international": [
        "['in', 'ter', 'nash', 'uh', 'nl']",
        "ANTRNXNL"
    ],
    "internet": [
        "['in', 'ter', 'net']",
        "ANTRNT"
    ],
    "interrupt": [
        "[verbin,tuh,ruhpt]",
        "ANTRPT"
    ],
    "interrupting": [
        "['verbin', 'tuh', 'ruhpt', 'ing']",
        "ANTRPTNK"
    ],
    "interstate": [
        "['adjectivein', 'ter', 'steyt']",
        "ANTRSTT"
    ],
    "intertwined": [
        "['in', 'ter', 'twahyn', 'd']",
        "ANTRTNT"
    ],
    "intervene": [
        "['in', 'ter', 'veen']",
        "ANTRFN"
    ],
    "intervention": [
        "[in,ter,ven,shuhn]",
        "ANTRFNXN"
    ],
    "interview": [
        "[in,ter,vyoo]",
        "ANTRF"
    ],
    "interviews": [
        "[in,ter,vyoo,s]",
        "ANTRFS"
    ],
    "intimate": [
        "['in', 'tuh', 'mit']",
        "ANTMT"
    ],
    "intimidated": [
        "[in,tim,i,deyt,d]",
        "ANTMTTT"
    ],
    "into": [
        "['in', 'too']",
        "ANT"
    ],
    "intoxicated": [
        "['in', 'tok', 'si', 'key', 'tid']",
        "ANTKSKTT"
    ],
    "intoxicating": [
        "[in,tok,si,key,ting]",
        "ANTKSKTNK"
    ],
    "intro": [
        "['in', 'troh']",
        "ANTR"
    ],
    "introduce": [
        "['in', 'truh', 'doos']",
        "ANTRTS"
    ],
    "introduced": [
        "['in', 'truh', 'doos', 'd']",
        "ANTRTST"
    ],
    "introduction": [
        "['in', 'truh', 'duhk', 'shuhn']",
        "ANTRTKXN"
    ],
    "intrude": [
        "[in,trood]",
        "ANTRT"
    ],
    "intuition": [
        "['in', 'too', 'ish', 'uhn']",
        "ANTXN"
    ],
    "invade": [
        "['in', 'veyd']",
        "ANFT"
    ],
    "invaded": [
        "['in', 'veyd', 'd']",
        "ANFTT"
    ],
    "invasion": [
        "[in,vey,zhuhn]",
        "ANFSN"
    ],
    "invent": [
        "[in,vent]",
        "ANFNT"
    ],
    "invented": [
        "['in', 'vent', 'ed']",
        "ANFNTT"
    ],
    "invention": [
        "[in,ven,shuhn]",
        "ANFNXN"
    ],
    "invest": [
        "['in', 'vest']",
        "ANFST"
    ],
    "invested": [
        "[in,vest,ed]",
        "ANFSTT"
    ],
    "investigation": [
        "['in', 'ves', 'ti', 'gey', 'shuhn']",
        "ANFSTKXN"
    ],
    "investing": [
        "['in', 'vest', 'ing']",
        "ANFSTNK"
    ],
    "investment": [
        "['in', 'vest', 'muhnt']",
        "ANFSTMNT"
    ],
    "investments": [
        "[in,vest,muhnt,s]",
        "ANFSTMNTS"
    ],
    "invincible": [
        "['in', 'vin', 'suh', 'buhl']",
        "ANFNSPL"
    ],
    "invisible": [
        "[in,viz,uh,buhl]",
        "ANFSPL"
    ],
    "invitation": [
        "[in,vi,tey,shuhn]",
        "ANFTXN"
    ],
    "invite": [
        "['verbin', 'vahyt']",
        "ANFT"
    ],
    "invited": [
        "['verbin', 'vahyt', 'd']",
        "ANFTT"
    ],
    "inviting": [
        "[in,vahy,ting]",
        "ANFTNK"
    ],
    "involve": [
        "[in,volv]",
        "ANFLF"
    ],
    "involved": [
        "['in', 'volvd']",
        "ANFLFT"
    ],
    "io": [
        "[ee,oh]",
        "A"
    ],
    "ion": [
        "['ahy', 'uhn']",
        "AN"
    ],
    "ipod": [
        "['ahy', 'pod']",
        "APT"
    ],
    "iran": [
        "['ih', 'ran']",
        "ARN"
    ],
    "iraq": [
        "['ih', 'rak']",
        "ARK"
    ],
    "irate": [
        "[ahy,reyt]",
        "ART"
    ],
    "irish": [
        "['ahy', 'rish']",
        "ARX"
    ],
    "irking": [
        "['urk', 'ing']",
        "ARKNK"
    ],
    "iron": [
        "['ahy', 'ern']",
        "ARN"
    ],
    "ironic": [
        "['ahy', 'ron', 'ik']",
        "ARNK"
    ],
    "irony": [
        "[ahy,ruh,nee]",
        "ARN"
    ],
    "irregular": [
        "[ih,reg,yuh,ler]",
        "ARKLR"
    ],
    "irrelevant": [
        "[ih,rel,uh,vuhnt]",
        "ARLFNT"
    ],
    "irreplaceable": [
        "[ir,i,pley,suh,buhl]",
        "ARPLSPL"
    ],
    "irritating": [
        "[ir,i,tey,ting]",
        "ARTTNK"
    ],
    "is": [
        "['iz']",
        "AS"
    ],
    "isaiah": [
        "[ahy,zey,uhor]",
        "AS"
    ],
    "isis": [
        "['ahy', 'sis']",
        "ASS"
    ],
    "islam": [
        "[is,lahm]",
        "ALM"
    ],
    "islamic": [
        "[is,lahm,ic]",
        "ALMK"
    ],
    "island": [
        "['ahy', 'luhnd']",
        "ALNT"
    ],
    "islands": [
        "['ahy', 'luhnd', 's']",
        "ALNTS"
    ],
    "isn't": [
        "['iz', 'uhnt']",
        "ASNNT"
    ],
    "issue": [
        "['ish', 'ooor']",
        "AS"
    ],
    "issues": [
        "['ish', 'ooor', 's']",
        "ASS"
    ],
    "it": [
        "['it']",
        "AT"
    ],
    "it'd": [
        "['it', 'uhd']",
        "ATTT"
    ],
    "it'll": [
        "['it', 'l']",
        "ATTL"
    ],
    "it's": [
        "['its']",
        "ATTS"
    ],
    "italian": [
        "[ih,tal,yuhn]",
        "ATLN"
    ],
    "italy": [
        "['it', 'l', 'ee']",
        "ATL"
    ],
    "itch": [
        "['ich']",
        "AX"
    ],
    "itching": [
        "['ich', 'ing']",
        "AXNK"
    ],
    "itchy": [
        "['ich', 'ee']",
        "AX"
    ],
    "its": [
        "['its']",
        "ATS"
    ],
    "itself": [
        "['it', 'self']",
        "ATSLF"
    ],
    "iv": [
        "['ahy', 'vee']",
        "AF"
    ],
    "ivory": [
        "[ahy,vuh,ree]",
        "AFR"
    ],
    "ivy": [
        "[ahy,vee]",
        "AF"
    ],
    "j": [
        "['jey', '']",
        "J"
    ],
    "j's": [
        [
            "jeys"
        ],
        "JJS"
    ],
    "jab": [
        "['jab']",
        "JP"
    ],
    "jabber": [
        "[jab,er]",
        "JPR"
    ],
    "jabs": [
        "['jab', 's']",
        "JPS"
    ],
    "jack": [
        "['jak']",
        "JK"
    ],
    "jackass": [
        "[jak,as]",
        "JKS"
    ],
    "jacked": [
        "[jakt]",
        "JKT"
    ],
    "jacket": [
        "['jak', 'it']",
        "JKT"
    ],
    "jackets": [
        "['jak', 'it', 's']",
        "JKTS"
    ],
    "jackie": [
        "['jak', 'ee']",
        "JK"
    ],
    "jacking": [
        "['jak', 'ing']",
        "JKNK"
    ],
    "jackknife": [
        "[jak,nahyf]",
        "JKKNF"
    ],
    "jackpot": [
        "['jak', 'pot']",
        "JKPT"
    ],
    "jacks": [
        "['jak', 's']",
        "JKS"
    ],
    "jackson": [
        "['jak', 'suhn']",
        "JKSN"
    ],
    "jackson's": [
        "['jak', 'suhn', \"'s\"]",
        "JKSNNS"
    ],
    "jacksons": [
        "['jak', 'suhn', 's']",
        "JKSNS"
    ],
    "jacob": [
        "['jey', 'kuhbfor1']",
        "JKP"
    ],
    "jacob's": [
        "[jey,kuhbfor1,'s]",
        "JKPPS"
    ],
    "jacobs": [
        "['jey', 'kuhbz']",
        "JKPS"
    ],
    "jacuzzi": [
        "['juh', 'koo', 'zee']",
        "JKS"
    ],
    "jaded": [
        "['jey', 'did']",
        "JTT"
    ],
    "jag": [
        "['jag']",
        "JK"
    ],
    "jagged": [
        "[jag,id]",
        "JKT"
    ],
    "jags": [
        "['jag', 's']",
        "JKS"
    ],
    "jaguar": [
        "['jag', 'wahr']",
        "JKR"
    ],
    "jail": [
        "['jeyl']",
        "JL"
    ],
    "jailhouse": [
        "[jeyl,hous]",
        "JLS"
    ],
    "jails": [
        "['jeyl', 's']",
        "JLS"
    ],
    "jam": [
        "['jam']",
        "JM"
    ],
    "jamaica": [
        "[juh,mey,kuh]",
        "JMK"
    ],
    "jamaican": [
        "['juh', 'mey', 'kuhn']",
        "JMKN"
    ],
    "james": [
        "['jeymz']",
        "JMS"
    ],
    "jammed": [
        "['jam', 'med']",
        "JMT"
    ],
    "jammies": [
        "['jam', 'eez']",
        "JMS"
    ],
    "jamming": [
        "['jam', 'ming']",
        "JMNK"
    ],
    "jams": [
        "[jamz]",
        "JMS"
    ],
    "jane": [
        "['jeyn']",
        "JN"
    ],
    "janet": [
        "['zha', 'nefor1']",
        "JNT"
    ],
    "jangle": [
        "[jang,guhl]",
        "JNKL"
    ],
    "january": [
        "['jan', 'yoo', 'er', 'ee']",
        "JNR"
    ],
    "japan": [
        "['juh', 'pan']",
        "JPN"
    ],
    "japanese": [
        "['jap', 'uh', 'neez']",
        "JPNS"
    ],
    "jar": [
        "['jahr']",
        "JR"
    ],
    "jars": [
        "[jahr,s]",
        "JRS"
    ],
    "jason": [
        "[jey,suhn]",
        "JSN"
    ],
    "jasper": [
        "['jas', 'per']",
        "JSPR"
    ],
    "jaw": [
        "['jaw']",
        "J"
    ],
    "jaws": [
        "['jaw', 's']",
        "JS"
    ],
    "jay": [
        "['jey']",
        "J"
    ],
    "jay's": [
        "[jey,'s]",
        "JS"
    ],
    "jays": [
        "['jey', 's']",
        "JS"
    ],
    "jazz": [
        "['jaz']",
        "JS"
    ],
    "jazzy": [
        "[jaz,ee]",
        "JS"
    ],
    "jealous": [
        "['jel', 'uhs']",
        "JLS"
    ],
    "jealousy": [
        "['jel', 'uh', 'see']",
        "JLS"
    ],
    "jean": [
        "['jeenorfor1']",
        "JN"
    ],
    "jeans": [
        "['jeenz']",
        "JNS"
    ],
    "jeep": [
        "['jeep']",
        "JP"
    ],
    "jeeps": [
        "[jeep,s]",
        "JPS"
    ],
    "jeez": [
        "['jeez']",
        "JS"
    ],
    "jefferson": [
        "['jef', 'er', 'suhn']",
        "JFRSN"
    ],
    "jehovah": [
        "[ji,hoh,vuh]",
        "JHF"
    ],
    "jell": [
        "[jel]",
        "JL"
    ],
    "jello": [
        "[jel,oh]",
        "JL"
    ],
    "jelly": [
        "['jel', 'ee']",
        "JL"
    ],
    "jenner": [
        "['jen', 'er']",
        "JNR"
    ],
    "jennifer": [
        "['jen', 'uh', 'fer']",
        "JNFR"
    ],
    "jenny": [
        "['jen', 'ee']",
        "JN"
    ],
    "jeopardize": [
        "['jep', 'er', 'dahyz']",
        "JPRTS"
    ],
    "jericho": [
        "[jer,i,koh]",
        "JRX"
    ],
    "jerk": [
        "['jurk']",
        "JRK"
    ],
    "jerking": [
        "[jurk,ing]",
        "JRKNK"
    ],
    "jerks": [
        "[jurk,s]",
        "JRKS"
    ],
    "jerome": [
        "[juh,rohm]",
        "JRM"
    ],
    "jerry": [
        "['jer', 'ee']",
        "JR"
    ],
    "jersey": [
        "['jur', 'zee']",
        "JRS"
    ],
    "jerseys": [
        "['jur', 'zee', 's']",
        "JRSS"
    ],
    "jerusalem": [
        "[ji,roo,suh,luhm]",
        "JRSLM"
    ],
    "jesse": [
        "['jes', 'ee']",
        "JS"
    ],
    "jesus": [
        "['jee', 'zuhs']",
        "JSS"
    ],
    "jet": [
        "['jet']",
        "JT"
    ],
    "jets": [
        "['jet', 's']",
        "JTS"
    ],
    "jew": [
        "['joo']",
        "J"
    ],
    "jewel": [
        "['joo', 'uhl']",
        "JL"
    ],
    "jeweler": [
        "['joo', 'uh', 'ler']",
        "JLR"
    ],
    "jewelers": [
        "['joo', 'uh', 'ler', 's']",
        "JLRS"
    ],
    "jewelry": [
        "['joo', 'uhl', 'ree']",
        "JLR"
    ],
    "jewelry's": [
        "['joo', 'uhl', 'ree', \"'s\"]",
        "JLRS"
    ],
    "jewels": [
        "['joo', 'uhl', 's']",
        "JLS"
    ],
    "jewish": [
        "['joo', 'ish']",
        "JX"
    ],
    "jews": [
        "['joo', 's']",
        "JS"
    ],
    "jiffy": [
        "['jif', 'ee']",
        "JF"
    ],
    "jig": [
        "[jig]",
        "JK"
    ],
    "jiggle": [
        "['jig', 'uhl']",
        "JKL"
    ],
    "jiggy": [
        "['jig', 'ee']",
        "JK"
    ],
    "jill": [
        "['jil']",
        "JL"
    ],
    "jimmy": [
        "['jim', 'ee']",
        "JM"
    ],
    "jingle": [
        "[jing,guhl]",
        "JNKL"
    ],
    "jive": [
        "['jahyv']",
        "JF"
    ],
    "job": [
        "['job']",
        "JP"
    ],
    "job's": [
        "[job,'s]",
        "JPPS"
    ],
    "jobs": [
        "['job', 's']",
        "JPS"
    ],
    "jock": [
        "[jok]",
        "JK"
    ],
    "jodeci": [
        [
            "joh",
            "dey",
            "see"
        ],
        "JTS"
    ],
    "joe": [
        "['joh']",
        "J"
    ],
    "jog": [
        "['jog']",
        "JK"
    ],
    "jogging": [
        "['jog', 'ging']",
        "JJNK"
    ],
    "john": [
        "['jon']",
        "JN"
    ],
    "johnny": [
        "['jon', 'ee']",
        "JN"
    ],
    "johns": [
        "[jonz]",
        "JNS"
    ],
    "johnson": [
        "[jon,suhn]",
        "JNSN"
    ],
    "join": [
        "['join']",
        "JN"
    ],
    "joint": [
        "['joint']",
        "JNT"
    ],
    "joints": [
        "[joint,s]",
        "JNTS"
    ],
    "joke": [
        "['johk']",
        "JK"
    ],
    "joker": [
        "['joh', 'ker']",
        "JKR"
    ],
    "jokers": [
        "[joh,ker,s]",
        "JKRS"
    ],
    "jokes": [
        "['johk', 's']",
        "JKS"
    ],
    "joking": [
        [
            "joh",
            "king"
        ],
        "JKNK"
    ],
    "jolly": [
        "['jol', 'ee']",
        "JL"
    ],
    "jones": [
        "[johnz]",
        "JNS"
    ],
    "jooks": [
        "[jook,s]",
        "JKS"
    ],
    "jordan": [
        "['jawr', 'dn']",
        "JRTN"
    ],
    "jordan's": [
        "[jawr,dn,'s]",
        "JRTNNS"
    ],
    "jordans": [
        "['jawr', 'dn', 's']",
        "JRTNS"
    ],
    "jot": [
        "[jot]",
        "JT"
    ],
    "journalists": [
        "[jur,nl,ist,s]",
        "JRNLSTS"
    ],
    "journey": [
        "['jur', 'nee']",
        "JRN"
    ],
    "joy": [
        "[joi]",
        "J"
    ],
    "joyce": [
        "[jois]",
        "JS"
    ],
    "juan": [
        "['wahn']",
        "JN"
    ],
    "judas": [
        "[joo,duhs]",
        "JTS"
    ],
    "judge": [
        "['juhj']",
        "JJ"
    ],
    "judges": [
        "[juhj,iz]",
        "JJS"
    ],
    "judgment": [
        "[juhj,muhnt]",
        "JTKMNT"
    ],
    "judo": [
        "[joo,doh]",
        "JT"
    ],
    "judy": [
        "['joo', 'dee']",
        "JT"
    ],
    "jug": [
        "['juhg']",
        "JK"
    ],
    "jugg": [
        [
            "juhg"
        ],
        "JK"
    ],
    "jugging": [
        "['juhg', 'ging']",
        "JKNK"
    ],
    "juggle": [
        "['juhg', 'uhl']",
        "JKL"
    ],
    "jugs": [
        "[juhg,s]",
        "JKS"
    ],
    "juice": [
        "['joos']",
        "JS"
    ],
    "juices": [
        "['joos', 's']",
        "JSS"
    ],
    "juicy": [
        "['joo', 'see']",
        "JS"
    ],
    "jujitsu": [
        "[joo,jit,soo]",
        "JJTS"
    ],
    "juke": [
        "[jook]",
        "JK"
    ],
    "julius": [
        "['jool', 'yuhs']",
        "JLS"
    ],
    "july": [
        "['joo', 'lahy']",
        "JL"
    ],
    "jumanji": [
        [
            "joo",
            "man",
            "jee"
        ],
        "JMNJ"
    ],
    "jump": [
        "['juhmp']",
        "JMP"
    ],
    "jumped": [
        "['juhmp', 'ed']",
        "JMPT"
    ],
    "jumper": [
        "['juhm', 'per']",
        "JMPR"
    ],
    "jumping": [
        "['juhmp', 'ing']",
        "JMPNK"
    ],
    "jumps": [
        "[juhmp,s]",
        "JMPS"
    ],
    "june": [
        "['joon']",
        "JN"
    ],
    "jungle": [
        "['juhng', 'guhl']",
        "JNKL"
    ],
    "jungles": [
        "[juhng,guhl,s]",
        "JNKLS"
    ],
    "junior": [
        "['joon', 'yer']",
        "JNR"
    ],
    "junk": [
        "['juhngk']",
        "JNK"
    ],
    "junkie": [
        "['juhng', 'kee']",
        "JNK"
    ],
    "junkies": [
        "['juhng', 'kee', 's']",
        "JNKS"
    ],
    "junky": [
        "['juhng', 'kee']",
        "JNK"
    ],
    "junkyard": [
        "['juhngk', 'yahrd']",
        "JNKRT"
    ],
    "jupiter": [
        "['joo', 'pi', 'ter']",
        "JPTR"
    ],
    "jurassic": [
        "['joo', 'ras', 'ik']",
        "JRSK"
    ],
    "jury": [
        "['joor', 'ee']",
        "JR"
    ],
    "just": [
        "['juhst']",
        "JST"
    ],
    "justice": [
        "[juhs,tis]",
        "JSTS"
    ],
    "justify": [
        "[juhs,tuh,fahy]",
        "JSTF"
    ],
    "justin": [
        "['juhs', 'tin']",
        "JSTN"
    ],
    "juvenile": [
        "['joo', 'vuh', 'nl']",
        "JFNL"
    ],
    "k": [
        "['key', '']",
        "K"
    ],
    "ka": [
        "[kah]",
        "K"
    ],
    "kaboom": [
        [
            "kah",
            "boom"
        ],
        "KPM"
    ],
    "kama": [
        "[kah,muh]",
        "KM"
    ],
    "kamikaze": [
        "['kah', 'mi', 'kah', 'zee']",
        "KMKS"
    ],
    "kangaroo": [
        "[kang,guh,roo]",
        "KNKR"
    ],
    "kansas": [
        "['kan', 'zuhs']",
        "KNSS"
    ],
    "kant": [
        "[kant]",
        "KNT"
    ],
    "karaoke": [
        "[kar,ee,oh,kee]",
        "KRK"
    ],
    "karat": [
        "['kar', 'uht']",
        "KRT"
    ],
    "karate": [
        "['kuh', 'rah', 'tee']",
        "KRT"
    ],
    "karats": [
        "['kar', 'uht', 's']",
        "KRTS"
    ],
    "kardashian": [
        [
            "kahr",
            "dash",
            "ee",
            "uhn"
        ],
        "KRTXN"
    ],
    "kareem": [
        "['kuh', 'reem']",
        "KRM"
    ],
    "karen": [
        "[kuh,ren]",
        "KRN"
    ],
    "karl": [
        "['kahrl']",
        "KRL"
    ],
    "karma": [
        "['kahr', 'muh']",
        "KRM"
    ],
    "kat": [
        "['kaht']",
        "KT"
    ],
    "katie": [
        "['key', 'tee']",
        "KT"
    ],
    "katrina": [
        "['kuh', 'tree', 'nuh']",
        "KTRN"
    ],
    "katy": [
        "['key', 'tee']",
        "KT"
    ],
    "kawasaki": [
        "['kah', 'wah', 'sah', 'kee']",
        "KSK"
    ],
    "kd": [
        [
            "key",
            "dee"
        ],
        "KT"
    ],
    "keen": [
        "[keen]",
        "KN"
    ],
    "keep": [
        "['keep']",
        "KP"
    ],
    "keeper": [
        "['kee', 'per']",
        "KPR"
    ],
    "keepers": [
        "['kee', 'per', 's']",
        "KPRS"
    ],
    "keeping": [
        "['kee', 'ping']",
        "KPNK"
    ],
    "keeps": [
        "['keep', 's']",
        "KPS"
    ],
    "keith": [
        "['keeth']",
        "K0"
    ],
    "kelly": [
        "['kel', 'ee']",
        "KL"
    ],
    "kemosabe": [
        [
            "keh",
            "mou",
            "sab"
        ],
        "KMSP"
    ],
    "ken": [
        "['ken']",
        "KN"
    ],
    "kendall": [
        "['ken', 'dl']",
        "KNTL"
    ],
    "kennedy": [
        "['ken', 'i', 'dee']",
        "KNT"
    ],
    "kennedy's": [
        "[ken,i,dee,'s]",
        "KNTS"
    ],
    "kenny": [
        "['ken', 'ee']",
        "KN"
    ],
    "kent": [
        "[kent]",
        "KNT"
    ],
    "kentucky": [
        "['kuhn', 'tuhk', 'ee']",
        "KNTK"
    ],
    "kept": [
        "['kept']",
        "KPT"
    ],
    "ketchup": [
        "['kech', 'uhp']",
        "KXP"
    ],
    "kettle": [
        "['ket', 'l']",
        "KTL"
    ],
    "kevin": [
        "['kev', 'in']",
        "KFN"
    ],
    "key": [
        "['kee']",
        "K"
    ],
    "keyboard": [
        "[kee,bawrd]",
        "KPRT"
    ],
    "keyed": [
        "[keed]",
        "KT"
    ],
    "keys": [
        "['kee', 's']",
        "KS"
    ],
    "khaki": [
        "[kak,ee]",
        "KK"
    ],
    "khakis": [
        "['kak', 'ee', 's']",
        "KKS"
    ],
    "khalifa": [
        "['kuh', 'leef', 'a']",
        "KLF"
    ],
    "ki": [
        "[kee]",
        "K"
    ],
    "ki's": [
        "['kee', \"'s\"]",
        "KS"
    ],
    "kick": [
        "['kik']",
        "KK"
    ],
    "kicked": [
        "['kik', 'ed']",
        "KKT"
    ],
    "kicker": [
        "['kik', 'er']",
        "KKR"
    ],
    "kicking": [
        "['kik', 'ing']",
        "KKNK"
    ],
    "kicks": [
        "['kik', 's']",
        "KKS"
    ],
    "kickstand": [
        "['kik', 'stand']",
        "KKSTNT"
    ],
    "kid": [
        "['kid']",
        "KT"
    ],
    "kid's": [
        "[kid,'s]",
        "KTTS"
    ],
    "kidd": [
        "['kid']",
        "KT"
    ],
    "kidding": [
        "['kid', 'ding']",
        "KTNK"
    ],
    "kidnap": [
        "['kid', 'nap']",
        "KTNP"
    ],
    "kidnapped": [
        "['kid', 'napt']",
        "KTNPT"
    ],
    "kidnappers": [
        "[kid,nap,pers]",
        "KTNPRS"
    ],
    "kidnapping": [
        "[kid,nap,ping]",
        "KTNPNK"
    ],
    "kidney": [
        "['kid', 'nee']",
        "KTN"
    ],
    "kidneys": [
        "['kid', 'nee', 's']",
        "KTNS"
    ],
    "kids": [
        "['kid', 's']",
        "KTS"
    ],
    "kill": [
        "['kil']",
        "KL"
    ],
    "killed": [
        "['kil', 'ed']",
        "KLT"
    ],
    "killer": [
        "['kil', 'er']",
        "KLR"
    ],
    "killers": [
        "['kil', 'er', 's']",
        "KLRS"
    ],
    "killing": [
        "['kil', 'ing']",
        "KLNK"
    ],
    "killings": [
        "[kil,ing,s]",
        "KLNKS"
    ],
    "kills": [
        "['kil', 's']",
        "KLS"
    ],
    "kilo": [
        "['kee', 'loh']",
        "KL"
    ],
    "kilo's": [
        "[kee,loh,'s]",
        "KLS"
    ],
    "kilos": [
        "['kee', 'loh', 's']",
        "KLS"
    ],
    "kilt": [
        "['kilt']",
        "KLT"
    ],
    "kim": [
        "['kim']",
        "KM"
    ],
    "kind": [
        "['kahynd']",
        "KNT"
    ],
    "kinder": [
        "['kahynd', 'er']",
        "KNTR"
    ],
    "kindergarten": [
        "[kin,der,gahr,tn]",
        "KNTRKRTN"
    ],
    "kindly": [
        "[kahynd,lee]",
        "KNTL"
    ],
    "kindness": [
        "['kahynd', 'nis']",
        "KNTNS"
    ],
    "kinds": [
        "[kahynd,s]",
        "KNTS"
    ],
    "kinfolk": [
        "['kin', 'fohk']",
        "KNFLK"
    ],
    "king": [
        "['king']",
        "KNK"
    ],
    "king's": [
        "[king,'s]",
        "KNKKS"
    ],
    "kingdom": [
        "[king,duhm]",
        "KNKTM"
    ],
    "kingpin": [
        "['king', 'pin']",
        "KNKPN"
    ],
    "kings": [
        "['kingz']",
        "KNKS"
    ],
    "kingston": [
        "['kingz', 'tuhn']",
        "KNKSTN"
    ],
    "kinks": [
        "[kingk,s]",
        "KNKS"
    ],
    "kinky": [
        "[king,kee]",
        "KNK"
    ],
    "kirk": [
        "[kurk]",
        "KRK"
    ],
    "kiss": [
        "['kis']",
        "KS"
    ],
    "kissed": [
        "['kis', 'ed']",
        "KST"
    ],
    "kisser": [
        "[kis,er]",
        "KSR"
    ],
    "kisses": [
        "['kis', 'es']",
        "KSS"
    ],
    "kissing": [
        "['kis', 'ing']",
        "KSNK"
    ],
    "kit": [
        "['kit']",
        "KT"
    ],
    "kitchen": [
        "['kich', 'uhn']",
        "KXN"
    ],
    "kitchens": [
        "['kich', 'uhn', 's']",
        "KXNS"
    ],
    "kite": [
        "['kahyt']",
        "KT"
    ],
    "kites": [
        "['kahyt', 's']",
        "KTS"
    ],
    "kitted": [
        "['kit', 'ted']",
        "KTT"
    ],
    "kitten": [
        "[kit,n]",
        "KTN"
    ],
    "kitty": [
        "['kit', 'ee']",
        "KT"
    ],
    "kiwi": [
        "['kee', 'wee']",
        "K"
    ],
    "kkk": [
        [
            "key",
            "key",
            "key"
        ],
        "KK"
    ],
    "klan": [
        "[klan]",
        "KLN"
    ],
    "kleenex": [
        "[klee,neks]",
        "KLNKS"
    ],
    "klondike": [
        "['klon', 'dahyk']",
        "KLNTK"
    ],
    "klumps": [
        [
            "kluhmp"
        ],
        "KLMPS"
    ],
    "knack": [
        "[nak]",
        "NK"
    ],
    "knapsack": [
        "[nap,sak]",
        "NPSK"
    ],
    "knee": [
        "['nee']",
        "N"
    ],
    "kneel": [
        "[neel]",
        "NL"
    ],
    "knees": [
        "['nee', 's']",
        "NS"
    ],
    "knew": [
        "['noo']",
        "N"
    ],
    "knife": [
        "['nahyf']",
        "NF"
    ],
    "knight": [
        "['nahyt']",
        "NT"
    ],
    "knives": [
        "['nahyvz']",
        "NFS"
    ],
    "knob": [
        "['nob']",
        "NP"
    ],
    "knock": [
        "['nok']",
        "NK"
    ],
    "knocked": [
        "['nok', 'ed']",
        "NKT"
    ],
    "knockers": [
        "['nok', 'er', 's']",
        "NKRS"
    ],
    "knocking": [
        "['nok', 'ing']",
        "NKNK"
    ],
    "knockout": [
        "['nok', 'out']",
        "NKT"
    ],
    "knocks": [
        "['nok', 's']",
        "NKS"
    ],
    "knot": [
        "['not']",
        "NT"
    ],
    "knots": [
        "['not', 's']",
        "NTS"
    ],
    "knotty": [
        "[not,ee]",
        "NT"
    ],
    "know": [
        "['noh']",
        "N"
    ],
    "knowing": [
        "['noh', 'ing']",
        "NNK"
    ],
    "knowledge": [
        "['nol', 'ij']",
        "NLJ"
    ],
    "known": [
        "['nohn']",
        "NN"
    ],
    "knows": [
        "['noh', 's']",
        "NS"
    ],
    "knuckle": [
        "['nuhk', 'uhl']",
        "NKL"
    ],
    "knuckles": [
        "['nuhk', 'uhl', 's']",
        "NKLS"
    ],
    "kobe": [
        "['koh', 'bee']",
        "KP"
    ],
    "kongo": [
        "[kong,goh]",
        "KNK"
    ],
    "kongos": [
        "[kong,goh,s]",
        "KNKS"
    ],
    "korea": [
        "['kuh', 'ree', 'uh']",
        "KR"
    ],
    "kors": [
        "[kawr,s]",
        "KRS"
    ],
    "kosher": [
        "[koh,sher]",
        "KXR"
    ],
    "kris": [
        "['krees']",
        "KRS"
    ],
    "kubrick": [
        "[koo,brik]",
        "KPRK"
    ],
    "kudos": [
        "[koo,dohz]",
        "KTS"
    ],
    "kunta": [
        [
            "koon",
            "tah"
        ],
        "KNT"
    ],
    "kush": [
        "['koosh']",
        "KX"
    ],
    "kylie": [
        "['kahy', 'lee']",
        "KL"
    ],
    "kyrie": [
        "['RomanCatholicChurch', '']",
        "KR"
    ],
    "l": [
        "['el', '']",
        "L"
    ],
    "lab": [
        "['lab']",
        "LP"
    ],
    "label": [
        "['ley', 'buhl']",
        "LPL"
    ],
    "labeled": [
        "[ley,buhl,ed]",
        "LPLT"
    ],
    "labels": [
        "['ley', 'buhl', 's']",
        "LPLS"
    ],
    "labor": [
        "['ley', 'ber']",
        "LPR"
    ],
    "lac": [
        "['lak']",
        "LK"
    ],
    "lace": [
        "['leys']",
        "LS"
    ],
    "laced": [
        "['leys', 'd']",
        "LST"
    ],
    "laces": [
        "['leys', 's']",
        "LSS"
    ],
    "lacing": [
        "['ley', 'sing']",
        "LSNK"
    ],
    "lack": [
        "['lak']",
        "LK"
    ],
    "lacking": [
        "['lak', 'ing']",
        "LKNK"
    ],
    "lacks": [
        "[lak,s]",
        "LKS"
    ],
    "lacs": [
        "['lak', 's']",
        "LKS"
    ],
    "ladder": [
        "['lad', 'er']",
        "LTR"
    ],
    "lade": [
        "[leyd]",
        "LT"
    ],
    "laden": [
        "[leyd,n]",
        "LTN"
    ],
    "lady": [
        "['ley', 'dee']",
        "LT"
    ],
    "lady's": [
        "[ley,dee,'s]",
        "LTS"
    ],
    "lag": [
        "[lag]",
        "LK"
    ],
    "laid": [
        "['leyd']",
        "LT"
    ],
    "lair": [
        "[lair]",
        "LR"
    ],
    "lake": [
        "['leyk']",
        "LK"
    ],
    "lakers": [
        "['ley', 'ker', 's']",
        "LKRS"
    ],
    "lakes": [
        "[leyk,s]",
        "LKS"
    ],
    "lam": [
        "['lam']",
        "LM"
    ],
    "lamb": [
        "['lam']",
        "LMP"
    ],
    "lamborghini": [
        [
            "lahm",
            "buhr",
            "gin",
            "ee"
        ],
        "LMPRKN"
    ],
    "lambs": [
        "['lam', 's']",
        "LMPS"
    ],
    "lame": [
        "['leym']",
        "LM"
    ],
    "lamed": [
        "[lah,mid]",
        "LMT"
    ],
    "lames": [
        "['leym', 's']",
        "LMS"
    ],
    "lamp": [
        "['lamp']",
        "LMP"
    ],
    "lamps": [
        "[lamp,s]",
        "LMPS"
    ],
    "lance": [
        "['lans']",
        "LNS"
    ],
    "land": [
        "['land']",
        "LNT"
    ],
    "landed": [
        "['lan', 'did']",
        "LNTT"
    ],
    "landing": [
        "['lan', 'ding']",
        "LNTNK"
    ],
    "landlord": [
        "['land', 'lawrd']",
        "LNTLRT"
    ],
    "lands": [
        "[land,s]",
        "LNTS"
    ],
    "lane": [
        "['leyn']",
        "LN"
    ],
    "lanes": [
        "['leyn', 's']",
        "LNS"
    ],
    "language": [
        "['lang', 'gwij']",
        "LNKJ"
    ],
    "lap": [
        "['lap']",
        "LP"
    ],
    "lapped": [
        "[lap,ped]",
        "LPT"
    ],
    "laps": [
        "['lap', 's']",
        "LPS"
    ],
    "laptop": [
        "['lap', 'top']",
        "LPTP"
    ],
    "laptops": [
        "[lap,top,s]",
        "LPTPS"
    ],
    "larceny": [
        "[lahr,suh,nee]",
        "LRSN"
    ],
    "large": [
        "['lahrj']",
        "LRJ"
    ],
    "larger": [
        "['lahrj', 'r']",
        "LRKR"
    ],
    "largest": [
        "[lahrj,st]",
        "LRJST"
    ],
    "larry": [
        "['lar', 'ee']",
        "LR"
    ],
    "las": [
        "['lah', 's']",
        "LS"
    ],
    "lasagna": [
        "['luh', 'zahn', 'yuh']",
        "LSN"
    ],
    "laser": [
        "['ley', 'zer']",
        "LSR"
    ],
    "lash": [
        "[lash]",
        "LX"
    ],
    "lashes": [
        "[lash,es]",
        "LXS"
    ],
    "lashing": [
        "['lash', 'ing']",
        "LXNK"
    ],
    "lassie": [
        "[las,ee]",
        "LS"
    ],
    "last": [
        "['last']",
        "LST"
    ],
    "lasting": [
        "['las', 'ting']",
        "LSTNK"
    ],
    "lasts": [
        "['last', 's']",
        "LSTS"
    ],
    "late": [
        "['leyt']",
        "LT"
    ],
    "lately": [
        "['leyt', 'lee']",
        "LTL"
    ],
    "later": [
        "['lei', 'ter']",
        "LTR"
    ],
    "latest": [
        "['ley', 'tist']",
        "LTST"
    ],
    "latex": [
        "['ley', 'teks']",
        "LTKS"
    ],
    "latin": [
        "[lat,n]",
        "LTN"
    ],
    "latinos": [
        "[luh,tee,noh,s]",
        "LTNS"
    ],
    "latitude": [
        "['lat', 'i', 'tood']",
        "LTTT"
    ],
    "latter": [
        "[lat,er]",
        "LTR"
    ],
    "laugh": [
        "['laf']",
        "LF"
    ],
    "laughed": [
        "['laf', 'ed']",
        "LFT"
    ],
    "laughing": [
        "['laf', 'ing']",
        "LFNK"
    ],
    "laughs": [
        "[laf,s]",
        "LFS"
    ],
    "laughter": [
        "[laf,ter]",
        "LFTR"
    ],
    "launch": [
        "[lawnch]",
        "LNX"
    ],
    "launching": [
        "['lawnch', 'ing']",
        "LNXNK"
    ],
    "laundering": [
        "[lawn,der,ing]",
        "LNTRNK"
    ],
    "laundry": [
        "['lawn', 'dree']",
        "LNTR"
    ],
    "laurens": [
        "[lawr,uhnz]",
        "LRNS"
    ],
    "lava": [
        "[lah,vuh]",
        "LF"
    ],
    "lavish": [
        "['lav', 'ish']",
        "LFX"
    ],
    "law": [
        "['law']",
        "L"
    ],
    "lawless": [
        "['law', 'lis']",
        "LLS"
    ],
    "lawn": [
        "['lawn']",
        "LN"
    ],
    "lawns": [
        "[lawn,s]",
        "LNS"
    ],
    "lawrence": [
        "[lawr,uhns]",
        "LRNS"
    ],
    "laws": [
        "['law', 's']",
        "LS"
    ],
    "lawsuit": [
        "['law', 'soot']",
        "LST"
    ],
    "lawyer": [
        "['law', 'yer']",
        "LR"
    ],
    "lawyers": [
        "['law', 'yer', 's']",
        "LRS"
    ],
    "lax": [
        "[laks]",
        "LKS"
    ],
    "lay": [
        "['ley']",
        "L"
    ],
    "layaway": [
        "['ley', 'uh', 'wey']",
        "L"
    ],
    "layer": [
        "[ley,er]",
        "LR"
    ],
    "laying": [
        "['ley', 'ing']",
        "LNK"
    ],
    "layover": [
        "['ley', 'oh', 'ver']",
        "LFR"
    ],
    "lays": [
        "[ley,s]",
        "LS"
    ],
    "lazy": [
        "['ley', 'zee']",
        "LS"
    ],
    "leach": [
        "[leech]",
        "LX"
    ],
    "lead": [
        "['leed']",
        "LT"
    ],
    "leader": [
        "['lee', 'der']",
        "LTR"
    ],
    "leaders": [
        "[lee,der,s]",
        "LTRS"
    ],
    "leading": [
        "[lee,ding]",
        "LTNK"
    ],
    "leads": [
        "['leed', 's']",
        "LTS"
    ],
    "leaf": [
        "['leef']",
        "LF"
    ],
    "leafs": [
        "[leef,s]",
        "LFS"
    ],
    "league": [
        "['leeg']",
        "LK"
    ],
    "leagues": [
        "[leeg,s]",
        "LKS"
    ],
    "leak": [
        "['leek']",
        "LK"
    ],
    "leaking": [
        "['leek', 'ing']",
        "LKNK"
    ],
    "leaks": [
        "[leek,s]",
        "LKS"
    ],
    "lean": [
        "['leen']",
        "LN"
    ],
    "leaned": [
        "[leen,ed]",
        "LNT"
    ],
    "leaning": [
        "['lee', 'ning']",
        "LNNK"
    ],
    "leap": [
        "[leep]",
        "LP"
    ],
    "leaping": [
        "['leep', 'ing']",
        "LPNK"
    ],
    "lear": [
        "['leer']",
        "LR"
    ],
    "learn": [
        "['lurn']",
        "LRN"
    ],
    "learned": [
        "['lur', 'nidfor13lurnd']",
        "LRNT"
    ],
    "learning": [
        "['lur', 'ning']",
        "LRNNK"
    ],
    "lease": [
        "['lees']",
        "LS"
    ],
    "leased": [
        "[lees,d]",
        "LST"
    ],
    "leash": [
        "['leesh']",
        "LX"
    ],
    "leasing": [
        "[lee,zing]",
        "LSNK"
    ],
    "least": [
        "['leest']",
        "LST"
    ],
    "leather": [
        "['leth', 'er']",
        "L0R"
    ],
    "leathers": [
        "[leth,er,s]",
        "L0RS"
    ],
    "leave": [
        "['leev']",
        "LF"
    ],
    "leaves": [
        "['leevz']",
        "LFS"
    ],
    "leaving": [
        "['lee', 'ving']",
        "LFNK"
    ],
    "lebanon": [
        "[leb,uh,nuhnorespeciallyfor1]",
        "LPNN"
    ],
    "lecture": [
        "[lek,cher]",
        "LKTR"
    ],
    "lectures": [
        "[lek,cher,s]",
        "LKTRS"
    ],
    "led": [
        "['led']",
        "LT"
    ],
    "ledge": [
        "['lej']",
        "LJ"
    ],
    "ledger": [
        "[lej,er]",
        "LJR"
    ],
    "lee": [
        "['lee']",
        "L"
    ],
    "lee's": [
        "[lee,'s]",
        "LS"
    ],
    "leech": [
        "['leech']",
        "LX"
    ],
    "leeches": [
        "['leech', 'es']",
        "LXS"
    ],
    "leer": [
        "['leer']",
        "LR"
    ],
    "left": [
        "['left']",
        "LFT"
    ],
    "leftovers": [
        "['left', 'oh', 'ver', 's']",
        "LFTFRS"
    ],
    "leg": [
        "['leg']",
        "LK"
    ],
    "legacy": [
        "['leg', 'uh', 'see']",
        "LKS"
    ],
    "legal": [
        "['lee', 'guhl']",
        "LKL"
    ],
    "legally": [
        "[lee,guhl,ly]",
        "LKL"
    ],
    "legend": [
        "['lej', 'uhnd']",
        "LJNT"
    ],
    "legendary": [
        "['lej', 'uhn', 'der', 'ee']",
        "LJNTR"
    ],
    "legends": [
        "[lej,uhnd,s]",
        "LJNTS"
    ],
    "legged": [
        "[leg,id]",
        "LKT"
    ],
    "legible": [
        "[lej,uh,buhl]",
        "LJPL"
    ],
    "legit": [
        "['luh', 'jit']",
        "LJT"
    ],
    "lego": [
        "['leg', 'oh']",
        "LK"
    ],
    "legs": [
        "['leg', 's']",
        "LKS"
    ],
    "leisure": [
        "[lee,zher]",
        "LSR"
    ],
    "lemme": [
        "['lem', 'ee']",
        "LM"
    ],
    "lemon": [
        "['lem', 'uhn']",
        "LMN"
    ],
    "lemonade": [
        "['lem', 'uh', 'neyd']",
        "LMNT"
    ],
    "lemons": [
        "['lem', 'uhn', 's']",
        "LMNS"
    ],
    "lend": [
        "[lend]",
        "LNT"
    ],
    "length": [
        "[lengkth]",
        "LNK0"
    ],
    "lennon": [
        "['len', 'uhn']",
        "LNN"
    ],
    "leno": [
        "['lee', 'noh']",
        "LN"
    ],
    "lenox": [
        "['len', 'uhks']",
        "LNKS"
    ],
    "lens": [
        "['lenz']",
        "LNS"
    ],
    "lenses": [
        "['lenz', 'es']",
        "LNSS"
    ],
    "lent": [
        "[lent]",
        "LNT"
    ],
    "leo": [
        "['lee', 'oh']",
        "L"
    ],
    "leon": [
        "[lee,on]",
        "LN"
    ],
    "leone": [
        "[lee,ohn]",
        "LN"
    ],
    "leopard": [
        "['lep', 'erd']",
        "LPRT"
    ],
    "leprechaun": [
        "['lep', 'ruh', 'kawn']",
        "LPRXN"
    ],
    "leprechauns": [
        "[lep,ruh,kawn,s]",
        "LPRXNS"
    ],
    "ler": [
        "['ler']",
        "LR"
    ],
    "lesbian": [
        "[lez,bee,uhn]",
        "LSPN"
    ],
    "lesbians": [
        "[lez,bee,uhn,s]",
        "LSPNS"
    ],
    "less": [
        "['les']",
        "LS"
    ],
    "lesser": [
        "['les', 'er']",
        "LSR"
    ],
    "lesson": [
        "['les', 'uhn']",
        "LSN"
    ],
    "lessons": [
        "['les', 'uhn', 's']",
        "LSNS"
    ],
    "let": [
        "['let']",
        "LT"
    ],
    "let's": [
        "['lets']",
        "LTTS"
    ],
    "lethal": [
        "['lee', 'thuhl']",
        "L0L"
    ],
    "lets": [
        "['let', 's']",
        "LTS"
    ],
    "letter": [
        "['let', 'er']",
        "LTR"
    ],
    "letterman": [
        "['let', 'er', 'man']",
        "LTRMN"
    ],
    "letters": [
        "['let', 'er', 's']",
        "LTRS"
    ],
    "letting": [
        "['let', 'ting']",
        "LTNK"
    ],
    "lettuce": [
        "['let', 'is']",
        "LTS"
    ],
    "levee": [
        "[lev,ee]",
        "LF"
    ],
    "levees": [
        "[lev,ee,s]",
        "LFS"
    ],
    "level": [
        "['lev', 'uhl']",
        "LFL"
    ],
    "levels": [
        "['lev', 'uhl', 's']",
        "LFLS"
    ],
    "lever": [
        "['lev', 'er']",
        "LFR"
    ],
    "leverage": [
        "[lev,er,ij]",
        "LFRJ"
    ],
    "levi's": [
        "[lee,vahyz]",
        "LFS"
    ],
    "levitate": [
        "['lev', 'i', 'teyt']",
        "LFTT"
    ],
    "lewis": [
        "['loo', 'is']",
        "LS"
    ],
    "lexus": [
        [
            "leks",
            "uhs"
        ],
        "LKSS"
    ],
    "li": [
        "['lee']",
        "L"
    ],
    "liable": [
        "[lahy,uh,buhl]",
        "LPL"
    ],
    "liar": [
        "['lahy', 'er']",
        "LR"
    ],
    "liars": [
        "['lahy', 'er', 's']",
        "LRS"
    ],
    "lib": [
        "['lib']",
        "LP"
    ],
    "liberated": [
        "['lib', 'uh', 'reyt', 'd']",
        "LPRTT"
    ],
    "liberty": [
        "['lib', 'er', 'tee']",
        "LPRT"
    ],
    "libido": [
        "[li,bee,doh]",
        "LPT"
    ],
    "libra": [
        "['lahy', 'bruh']",
        "LPR"
    ],
    "library": [
        "['lahy', 'brer', 'ee']",
        "LPRR"
    ],
    "lice": [
        "['lahys']",
        "LS"
    ],
    "license": [
        "['lahy', 'suhns']",
        "LSNS"
    ],
    "lick": [
        "['lik']",
        "LK"
    ],
    "licked": [
        "['lik', 'ed']",
        "LKT"
    ],
    "licking": [
        "['lik', 'ing']",
        "LKNK"
    ],
    "licks": [
        "['lik', 's']",
        "LKS"
    ],
    "licorice": [
        "[lik,er,ish]",
        "LKRS"
    ],
    "lid": [
        "['lid']",
        "LT"
    ],
    "lids": [
        "[lid,s]",
        "LTS"
    ],
    "lie": [
        "['lahy']",
        "L"
    ],
    "lied": [
        "['lahyd']",
        "LT"
    ],
    "lies": [
        "['lahy', 's']",
        "LS"
    ],
    "lieutenant": [
        "['loo', 'ten', 'uhnt']",
        "LTNNT"
    ],
    "lieutenants": [
        "[loo,ten,uhnt,s]",
        "LTNNTS"
    ],
    "life": [
        "['lahyf']",
        "LF"
    ],
    "life's": [
        "['lahyf', \"'s\"]",
        "LFS"
    ],
    "lifeguard": [
        "['lahyf', 'gahrd']",
        "LFKRT"
    ],
    "lifeless": [
        "[lahyf,lis]",
        "LFLS"
    ],
    "lifers": [
        "[lahy,fer,s]",
        "LFRS"
    ],
    "lifestyle": [
        "['lahyf', 'stahyl']",
        "LFSTL"
    ],
    "lifestyles": [
        "[lahyf,stahyl,s]",
        "LFSTLS"
    ],
    "lifetime": [
        "['lahyf', 'tahym']",
        "LFTM"
    ],
    "lift": [
        "['lift']",
        "LFT"
    ],
    "lifted": [
        "['lift', 'ed']",
        "LFTT"
    ],
    "lifting": [
        "[lift,ing]",
        "LFTNK"
    ],
    "light": [
        "['lahyt']",
        "LT"
    ],
    "light's": [
        "['lahyt', \"'s\"]",
        "LTTS"
    ],
    "lighten": [
        "['lahyt', 'n']",
        "LTN"
    ],
    "lightening": [
        "[lahyt,n,ing]",
        "LTNNK"
    ],
    "lighter": [
        "['lahy', 'ter']",
        "LTR"
    ],
    "lighters": [
        "[lahy,ter,s]",
        "LTRS"
    ],
    "lighthouse": [
        "['lahyt', 'hous']",
        "L0S"
    ],
    "lighting": [
        "['lahy', 'ting']",
        "LTNK"
    ],
    "lightly": [
        "['lahyt', 'lee']",
        "LTL"
    ],
    "lightning": [
        "['lahyt', 'ning']",
        "LTNNK"
    ],
    "lights": [
        "['lahyts']",
        "LTS"
    ],
    "like": [
        "['lahyk']",
        "LK"
    ],
    "like's": [
        "[lahyk,'s]",
        "LKS"
    ],
    "liked": [
        "['lahyk', 'd']",
        "LKT"
    ],
    "likely": [
        "[lahyk,lee]",
        "LKL"
    ],
    "likes": [
        "['lahyk', 's']",
        "LKS"
    ],
    "liking": [
        "['lahy', 'king']",
        "LKNK"
    ],
    "lima": [
        "['lee', 'muh']",
        "LM"
    ],
    "limb": [
        "[lim]",
        "LMP"
    ],
    "limbo": [
        "['lim', 'boh']",
        "LMP"
    ],
    "limbs": [
        "[lim,s]",
        "LMPS"
    ],
    "lime": [
        "['lahym']",
        "LM"
    ],
    "limelight": [
        "[lahym,lahyt]",
        "LMLT"
    ],
    "limit": [
        "['lim', 'it']",
        "LMT"
    ],
    "limitation": [
        "['lim', 'i', 'tey', 'shuhn']",
        "LMTXN"
    ],
    "limitations": [
        "[lim,i,tey,shuhn,s]",
        "LMTXNS"
    ],
    "limited": [
        "[lim,i,tid]",
        "LMTT"
    ],
    "limitless": [
        "[lim,it,lis]",
        "LMTLS"
    ],
    "limits": [
        "['lim', 'it', 's']",
        "LMTS"
    ],
    "limo": [
        "['lim', 'oh']",
        "LM"
    ],
    "limousine": [
        "['lim', 'uh', 'zeen']",
        "LMSN"
    ],
    "limp": [
        "['limp']",
        "LMP"
    ],
    "limping": [
        "['limp', 'ing']",
        "LMPNK"
    ],
    "lincoln": [
        "['ling', 'kuhn']",
        "LNKLN"
    ],
    "lincolns": [
        "[ling,kuhn,s]",
        "LNKLNS"
    ],
    "lindsay": [
        "['lind', 'zee']",
        "LNTS"
    ],
    "line": [
        "['lahyn']",
        "LN"
    ],
    "lined": [
        "['lahyn', 'd']",
        "LNT"
    ],
    "linen": [
        "['lin', 'uhn']",
        "LNN"
    ],
    "linens": [
        "[lin,uhn,s]",
        "LNNS"
    ],
    "lines": [
        "['lahyn', 's']",
        "LNS"
    ],
    "ling": [
        "['ling']",
        "LNK"
    ],
    "lingerie": [
        "['lahn', 'zhuh', 'rey']",
        "LNKR"
    ],
    "lingo": [
        "['ling', 'goh']",
        "LNK"
    ],
    "lining": [
        "['lahy', 'ning']",
        "LNNK"
    ],
    "link": [
        "['lingk']",
        "LNK"
    ],
    "linked": [
        "['lingkt']",
        "LNKT"
    ],
    "linking": [
        "['lingk', 'ing']",
        "LNKNK"
    ],
    "links": [
        "['lingks']",
        "LNKS"
    ],
    "lint": [
        "['lint']",
        "LNT"
    ],
    "lion": [
        "['lahy', 'uhn']",
        "LN"
    ],
    "lion's": [
        "[lahy,uhn,'s]",
        "LNNS"
    ],
    "lionhearted": [
        "[lahy,uhn,hahr,tid]",
        "LNRTT"
    ],
    "lions": [
        "['lahy', 'uhnz']",
        "LNS"
    ],
    "lip": [
        "['lip']",
        "LP"
    ],
    "lips": [
        "['lip', 's']",
        "LPS"
    ],
    "lipstick": [
        "['lip', 'stik']",
        "LPSTK"
    ],
    "liquid": [
        "['lik', 'wid']",
        "LKT"
    ],
    "liquor": [
        "['lik', 'erorfor3']",
        "LKR"
    ],
    "liquorice": [
        "['lik', 'uh', 'rish']",
        "LKRS"
    ],
    "liquors": [
        "[lik,erorfor3,s]",
        "LKRS"
    ],
    "lis": [
        "['lee', 's']",
        "LS"
    ],
    "lisa": [
        "['lee', 'suh']",
        "LS"
    ],
    "list": [
        "['list']",
        "LST"
    ],
    "listen": [
        "['lis', 'uhn']",
        "LSTN"
    ],
    "listened": [
        "['lis', 'uhn', 'ed']",
        "LSTNT"
    ],
    "listening": [
        "['lis', 'uhn', 'ing']",
        "LSTNNK"
    ],
    "listens": [
        "[lis,uhn,s]",
        "LSTNS"
    ],
    "lists": [
        "[lists]",
        "LSTS"
    ],
    "lit": [
        "['lit']",
        "LT"
    ],
    "lite": [
        "[lahyt]",
        "LT"
    ],
    "liter": [
        "['lee', 'ter']",
        "LTR"
    ],
    "literally": [
        "['lit', 'er', 'uh', 'lee']",
        "LTRL"
    ],
    "literary": [
        "[lit,uh,rer,ee]",
        "LTRR"
    ],
    "litigation": [
        "[lit,i,gey,shuhn]",
        "LTKXN"
    ],
    "litter": [
        "[lit,er]",
        "LTR"
    ],
    "little": [
        "['lit', 'l']",
        "LTL"
    ],
    "live": [
        "['liv']",
        "LF"
    ],
    "lived": [
        "['lahyvd']",
        "LFT"
    ],
    "liver": [
        "['liv', 'er']",
        "LFR"
    ],
    "lives": [
        "['lahyvz']",
        "LFS"
    ],
    "livest": [
        "[lahyv,st]",
        "LFST"
    ],
    "livid": [
        "['liv', 'id']",
        "LFT"
    ],
    "living": [
        "['liv', 'ing']",
        "LFNK"
    ],
    "lizard": [
        "[liz,erd]",
        "LSRT"
    ],
    "llama": [
        "['lah', 'muh']",
        "LM"
    ],
    "llamas": [
        "[lah,muh,s]",
        "LMS"
    ],
    "load": [
        "['lohd']",
        "LT"
    ],
    "loaded": [
        "['loh', 'did']",
        "LTT"
    ],
    "loading": [
        "['loh', 'ding']",
        "LTNK"
    ],
    "loads": [
        "[lohd,s]",
        "LTS"
    ],
    "loaf": [
        "['lohf']",
        "LF"
    ],
    "loafers": [
        "['loh', 'fer', 's']",
        "LFRS"
    ],
    "loafs": [
        "[lohf,s]",
        "LFS"
    ],
    "loan": [
        "[lohn]",
        "LN"
    ],
    "loaned": [
        "[lohn,ed]",
        "LNT"
    ],
    "loaner": [
        "['loh', 'ner']",
        "LNR"
    ],
    "loans": [
        "['lohn', 's']",
        "LNS"
    ],
    "lobby": [
        "['lob', 'ee']",
        "LP"
    ],
    "lobster": [
        "['lob', 'ster']",
        "LPSTR"
    ],
    "lobsters": [
        "['lob', 'ster', 's']",
        "LPSTRS"
    ],
    "local": [
        "['loh', 'kuhl']",
        "LKL"
    ],
    "locals": [
        "[loh,kuhl,s]",
        "LKLS"
    ],
    "locate": [
        "[loh,keyt]",
        "LKT"
    ],
    "location": [
        "['loh', 'key', 'shuhn']",
        "LKXN"
    ],
    "locations": [
        "[loh,key,shuhn,s]",
        "LKXNS"
    ],
    "loch": [
        "[lok]",
        "LX"
    ],
    "lock": [
        "['lok']",
        "LK"
    ],
    "lockdown": [
        "['lok', 'doun']",
        "LKTN"
    ],
    "locked": [
        "['lok', 'ed']",
        "LKT"
    ],
    "locker": [
        "['lok', 'er']",
        "LKR"
    ],
    "locking": [
        "['lok', 'ing']",
        "LKNK"
    ],
    "lockjaw": [
        "['lok', 'jaw']",
        "LK"
    ],
    "locks": [
        "['lok', 's']",
        "LKS"
    ],
    "locksmith": [
        "[lok,smith]",
        "LKSM0"
    ],
    "loco": [
        "[loh,koh]",
        "LK"
    ],
    "locomotion": [
        "[loh,kuh,moh,shuhn]",
        "LKMXN"
    ],
    "locust": [
        "[loh,kuhst]",
        "LKST"
    ],
    "loft": [
        "['lawft']",
        "LFT"
    ],
    "log": [
        "['lawg']",
        "LK"
    ],
    "logic": [
        "['loj', 'ik']",
        "LJK"
    ],
    "logo": [
        "['loh', 'goh']",
        "LK"
    ],
    "logos": [
        "[loh,gos]",
        "LKS"
    ],
    "logs": [
        "[lawg,s]",
        "LKS"
    ],
    "lol": [
        "['el', 'oh', 'elor']",
        "LL"
    ],
    "lollipop": [
        "['lol', 'ee', 'pop']",
        "LLPP"
    ],
    "lolly": [
        "[lol,ee]",
        "LL"
    ],
    "lolo": [
        "[loh,loh]",
        "LL"
    ],
    "lombardi": [
        "['lom', 'bahr', 'dee']",
        "LMPRT"
    ],
    "london": [
        "['luhn', 'duhn']",
        "LNTN"
    ],
    "lone": [
        "['lohn']",
        "LN"
    ],
    "lonely": [
        "['lohn', 'lee']",
        "LNL"
    ],
    "loner": [
        "['loh', 'ner']",
        "LNR"
    ],
    "long": [
        "['lawng']",
        "LNK"
    ],
    "longer": [
        "['lawng', 'er']",
        "LNKR"
    ],
    "longest": [
        "[lawng,est]",
        "LNJST"
    ],
    "longevity": [
        "['lon', 'jev', 'i', 'tee']",
        "LNJFT"
    ],
    "longing": [
        "[lawng,ing]",
        "LNJNK"
    ],
    "longitude": [
        "['lon', 'ji', 'tood']",
        "LNJTT"
    ],
    "look": [
        "['look']",
        "LK"
    ],
    "look's": [
        "['look', \"'s\"]",
        "LKKS"
    ],
    "looked": [
        "['look', 'ed']",
        "LKT"
    ],
    "looking": [
        "['look', 'ing']",
        "LKNK"
    ],
    "lookouts": [
        "[look,out,s]",
        "LKTS"
    ],
    "looks": [
        "['look', 's']",
        "LKS"
    ],
    "loop": [
        "['loop']",
        "LP"
    ],
    "loops": [
        "[loop,s]",
        "LPS"
    ],
    "loose": [
        "['loos']",
        "LS"
    ],
    "loosen": [
        "['loo', 'suhn']",
        "LSN"
    ],
    "looser": [
        "['loos', 'r']",
        "LSR"
    ],
    "loot": [
        "['loot']",
        "LT"
    ],
    "lopes": [
        "[lohp,s]",
        "LPS"
    ],
    "lord": [
        "['lawrd']",
        "LRT"
    ],
    "lord's": [
        "['lawrd', \"'s\"]",
        "LRTTS"
    ],
    "lords": [
        "[lawrd,s]",
        "LRTS"
    ],
    "lose": [
        "['looz']",
        "LS"
    ],
    "loser": [
        "['loo', 'zer']",
        "LSR"
    ],
    "losers": [
        "[loo,zer,s]",
        "LSRS"
    ],
    "loses": [
        "['looz', 's']",
        "LSS"
    ],
    "losing": [
        "['loo', 'zing']",
        "LSNK"
    ],
    "loss": [
        "['laws']",
        "LS"
    ],
    "losses": [
        "['laws', 'es']",
        "LSS"
    ],
    "lost": [
        "['lawst']",
        "LST"
    ],
    "lot": [
        "['lot']",
        "LT"
    ],
    "lotion": [
        "['loh', 'shuhn']",
        "LXN"
    ],
    "lots": [
        "['lot', 's']",
        "LTS"
    ],
    "lotta": [
        "['lot', 'uh']",
        "LT"
    ],
    "lottery": [
        "['lot', 'uh', 'ree']",
        "LTR"
    ],
    "lotto": [
        "['lot', 'oh']",
        "LT"
    ],
    "lotus": [
        "['loh', 'tuhs']",
        "LTS"
    ],
    "lou": [
        "['loo']",
        "L"
    ],
    "loud": [
        "['loud']",
        "LT"
    ],
    "louder": [
        "['loud', 'er']",
        "LTR"
    ],
    "loudest": [
        "['loud', 'est']",
        "LTST"
    ],
    "loudly": [
        "[loud,ly]",
        "LTL"
    ],
    "louie": [
        "['loo', 'ee']",
        "L"
    ],
    "louis": [
        "['loo', 'ee']",
        "LS"
    ],
    "louisiana": [
        "['loo', 'ee', 'zee', 'an', 'uh']",
        "LSN"
    ],
    "louisville": [
        "[loo,ee,vil]",
        "LSFL"
    ],
    "lounge": [
        "[lounj]",
        "LNJ"
    ],
    "lounging": [
        "[loun,jing]",
        "LNJNK"
    ],
    "louvre": [
        "[loo,ver]",
        "LFR"
    ],
    "love": [
        "['luhv']",
        "LF"
    ],
    "love's": [
        "['luhv', \"'s\"]",
        "LFS"
    ],
    "loved": [
        "['luhvd']",
        "LFT"
    ],
    "lovely": [
        "['luhv', 'lee']",
        "LFL"
    ],
    "lover": [
        "['luhv', 'er']",
        "LFR"
    ],
    "lovers": [
        "['luhv', 'er', 's']",
        "LFRS"
    ],
    "loves": [
        "['luhv', 's']",
        "LFS"
    ],
    "loving": [
        "['luhv', 'ing']",
        "LFNK"
    ],
    "low": [
        "['loh']",
        "L"
    ],
    "lower": [
        "['loh', 'er']",
        "LR"
    ],
    "lowest": [
        "['loh', 'est']",
        "LST"
    ],
    "lowry": [
        "['lou', 'ree']",
        "LR"
    ],
    "lows": [
        "[loh,s]",
        "LS"
    ],
    "lox": [
        "[loks]",
        "LKS"
    ],
    "loyal": [
        "['loi', 'uhl']",
        "LL"
    ],
    "loyalty": [
        "['loi', 'uhl', 'tee']",
        "LLT"
    ],
    "ls": [
        "['el']",
        "LS"
    ],
    "lu": [
        "[loo]",
        "L"
    ],
    "lube": [
        "[loob]",
        "LP"
    ],
    "lucas": [
        "['loo', 'kuhs']",
        "LKS"
    ],
    "lucifer": [
        "['loo', 'suh', 'fer']",
        "LSFR"
    ],
    "luck": [
        "['luhk']",
        "LK"
    ],
    "luckily": [
        "[luhk,uh,lee]",
        "LKL"
    ],
    "lucky": [
        "['luhk', 'ee']",
        "LK"
    ],
    "lucy": [
        "['loo', 'see']",
        "LS"
    ],
    "luda": [
        [
            "loo",
            "duh"
        ],
        "LT"
    ],
    "ludicrous": [
        "[loo,di,kruhs]",
        "LTKRS"
    ],
    "lug": [
        "['luhg']",
        "LK"
    ],
    "luggage": [
        "['luhg', 'ij']",
        "LKJ"
    ],
    "luke": [
        "[look]",
        "LK"
    ],
    "lukewarm": [
        "[look,wawrm]",
        "LKRM"
    ],
    "lullaby": [
        "['luhl', 'uh', 'bahy']",
        "LLP"
    ],
    "lumber": [
        "['luhm', 'ber']",
        "LMPR"
    ],
    "lump": [
        "[luhmp]",
        "LMP"
    ],
    "lumps": [
        "['luhmp', 's']",
        "LMPS"
    ],
    "lunatic": [
        "['loo', 'nuh', 'tik']",
        "LNTK"
    ],
    "lunatics": [
        "[loo,nuh,tik,s]",
        "LNTKS"
    ],
    "lunch": [
        "['luhnch']",
        "LNX"
    ],
    "lunchtime": [
        "[luhnch,tahym]",
        "LNKTM"
    ],
    "lung": [
        "['luhng']",
        "LNK"
    ],
    "lunger": [
        "[luhng,er]",
        "LNKR"
    ],
    "lungs": [
        "['luhng', 's']",
        "LNKS"
    ],
    "lure": [
        "[loor]",
        "LR"
    ],
    "lurk": [
        "['lurk']",
        "LRK"
    ],
    "lurking": [
        "['lurk', 'ing']",
        "LRKNK"
    ],
    "lust": [
        "['luhst']",
        "LST"
    ],
    "lusting": [
        "[luhst,ing]",
        "LSTNK"
    ],
    "luther": [
        "['loo', 'ther']",
        "L0R"
    ],
    "luxury": [
        "['luhk', 'shuh', 'ree']",
        "LKSR"
    ],
    "lye": [
        "[lahy]",
        "L"
    ],
    "lying": [
        "['lahy', 'ing']",
        "LNK"
    ],
    "lynch": [
        "[linch]",
        "LNX"
    ],
    "lyrical": [
        "['lir', 'ik', 'al']",
        "LRKL"
    ],
    "lyrically": [
        "[lir,ik,ally]",
        "LRKL"
    ],
    "lyrics": [
        "['lir', 'ik', 's']",
        "LRKS"
    ],
    "m": [
        "['em', '']",
        "M"
    ],
    "ma": [
        "['mah']",
        "M"
    ],
    "ma'am": [
        "['mam']",
        "MM"
    ],
    "ma's": [
        "[mah,'s]",
        "MS"
    ],
    "mac": [
        "['mak']",
        "MK"
    ],
    "mac's": [
        "[mak,'s]",
        "MKKS"
    ],
    "macarena": [
        "['mah', 'kuh', 'rey', 'nuh']",
        "MKRN"
    ],
    "macaroni": [
        "['mak', 'uh', 'roh', 'nee']",
        "MKRN"
    ],
    "macaulay": [
        "['muh', 'kaw', 'lee']",
        "MKL"
    ],
    "mace": [
        "['meys']",
        "MS"
    ],
    "machete": [
        "['muh', 'shet', 'ee']",
        "MXT"
    ],
    "machine": [
        "['muh', 'sheen']",
        "MXN"
    ],
    "machines": [
        "['muh', 'sheen', 's']",
        "MXNS"
    ],
    "macho": [
        "[mah,choh]",
        "MK"
    ],
    "mack": [
        "['mak']",
        "MK"
    ],
    "macking": [
        "['mak', 'ing']",
        "MKNK"
    ],
    "macs": [
        "['mak', 's']",
        "MKS"
    ],
    "mad": [
        "['mad']",
        "MT"
    ],
    "madden": [
        "['mad', 'n']",
        "MTN"
    ],
    "madder": [
        "[mad,er]",
        "MTR"
    ],
    "made": [
        "['meyd']",
        "MT"
    ],
    "madison": [
        "['mad', 'uh', 'suhn']",
        "MTSN"
    ],
    "madness": [
        "['mad', 'nis']",
        "MTNS"
    ],
    "madonna": [
        "['muh', 'don', 'uh']",
        "MTN"
    ],
    "mae": [
        "[mey]",
        "M"
    ],
    "mafia": [
        "['mah', 'fee', 'uh']",
        "MF"
    ],
    "mag": [
        "['mag']",
        "MK"
    ],
    "magazine": [
        "['mag', 'uh', 'zeen']",
        "MKSN"
    ],
    "magazines": [
        "['mag', 'uh', 'zeen', 's']",
        "MKSNS"
    ],
    "maggots": [
        "['mag', 'uht', 's']",
        "MKTS"
    ],
    "magic": [
        "['maj', 'ik']",
        "MJK"
    ],
    "magical": [
        "['maj', 'i', 'kuhl']",
        "MJKL"
    ],
    "magician": [
        "['muh', 'jish', 'uhn']",
        "MJSN"
    ],
    "magnet": [
        "[mag,nit]",
        "MNT"
    ],
    "magnificent": [
        "[mag,nif,uh,suhnt]",
        "MNFSNT"
    ],
    "magnolia": [
        "['mag', 'nohl', 'yuh']",
        "MNL"
    ],
    "magnum": [
        "['mag', 'nuhm']",
        "MNM"
    ],
    "magnums": [
        "['mag', 'nuhm', 's']",
        "MNMS"
    ],
    "mags": [
        "['mag', 's']",
        "MKS"
    ],
    "maid": [
        "['meyd']",
        "MT"
    ],
    "maids": [
        "[meyd,s]",
        "MTS"
    ],
    "mail": [
        "['meyl']",
        "ML"
    ],
    "mailbox": [
        "[meyl,boks]",
        "MLPKS"
    ],
    "mailman": [
        "[meyl,man]",
        "MLMN"
    ],
    "mails": [
        "[meyl,s]",
        "MLS"
    ],
    "maim": [
        "[meym]",
        "MM"
    ],
    "main": [
        "['meyn']",
        "MN"
    ],
    "maine": [
        "['meyn']",
        "MN"
    ],
    "mainly": [
        "[meyn,lee]",
        "MNL"
    ],
    "mainstream": [
        "[meyn,streem]",
        "MNSTRM"
    ],
    "maintain": [
        "['meyn', 'teyn']",
        "MNTN"
    ],
    "maintaining": [
        "[meyn,teyn,ing]",
        "MNTNNK"
    ],
    "maintenance": [
        "[meyn,tuh,nuhns]",
        "MNTNNS"
    ],
    "maison": [
        [
            "mey",
            "zuhn"
        ],
        "MSN"
    ],
    "majestic": [
        "[muh,jes,tik]",
        "MJSTK"
    ],
    "majesty": [
        "['maj', 'uh', 'stee']",
        "MJST"
    ],
    "major": [
        "['mey', 'jer']",
        "MJR"
    ],
    "majority": [
        "['muh', 'jawr', 'i', 'tee']",
        "MJRT"
    ],
    "majors": [
        "[mey,jer,s]",
        "MJRS"
    ],
    "make": [
        "['meyk']",
        "MK"
    ],
    "makeover": [
        "['meyk', 'oh', 'ver']",
        "MKFR"
    ],
    "maker": [
        "['mey', 'ker']",
        "MKR"
    ],
    "makes": [
        "['meyk', 's']",
        "MKS"
    ],
    "makeup": [
        "['meyk', 'uhp']",
        "MKP"
    ],
    "making": [
        "['mey', 'king']",
        "MKNK"
    ],
    "malaria": [
        "[muh,lair,ee,uh]",
        "MLR"
    ],
    "malcom": [
        [
            "mal",
            "kuhm"
        ],
        "MLKM"
    ],
    "male": [
        "[meyl]",
        "ML"
    ],
    "males": [
        "[meyl,s]",
        "MLS"
    ],
    "mali": [
        "[mah,lee]",
        "ML"
    ],
    "malice": [
        "['mal', 'is']",
        "MLS"
    ],
    "malik": [
        "[mah,lik]",
        "MLK"
    ],
    "mall": [
        "['mawl']",
        "ML"
    ],
    "malls": [
        "[mawl,s]",
        "MLS"
    ],
    "malo": [
        "['de dolo -', 'didoh', 'lohmal', 'oh']",
        "ML"
    ],
    "malone": [
        "['muh', 'lohn']",
        "MLN"
    ],
    "mama": [
        "['mah', 'muh']",
        "MM"
    ],
    "mama's": [
        "['mah', 'muh', \"'s\"]",
        "MMS"
    ],
    "mamas": [
        "[mah,muh,s]",
        "MMS"
    ],
    "mamba": [
        "[mahm,bah]",
        "MMP"
    ],
    "mamma": [
        "['mah', 'muh']",
        "MM"
    ],
    "mammal": [
        "[mam,uhl]",
        "MML"
    ],
    "mammy": [
        "[mam,ee]",
        "MM"
    ],
    "man": [
        "['man']",
        "MN"
    ],
    "man's": [
        "['man', \"'s\"]",
        "MNNS"
    ],
    "manage": [
        "['man', 'ij']",
        "MNJ"
    ],
    "managed": [
        "[man,ij,d]",
        "MNJT"
    ],
    "management": [
        "[man,ij,muhnt]",
        "MNJMNT"
    ],
    "manager": [
        "['man', 'i', 'jer']",
        "MNKR"
    ],
    "managers": [
        "['man', 'i', 'jer', 's']",
        "MNKRS"
    ],
    "mandarin": [
        "[man,duh,rin]",
        "MNTRN"
    ],
    "mandatory": [
        "['man', 'duh', 'tawr', 'ee']",
        "MNTTR"
    ],
    "mane": [
        "['meyn']",
        "MN"
    ],
    "mane's": [
        "['meyn', \"'s\"]",
        "MNS"
    ],
    "maneuver": [
        "['muh', 'noo', 'ver']",
        "MNFR"
    ],
    "mango": [
        "[mang,goh]",
        "MNK"
    ],
    "manhattan": [
        "[man,hat,n]",
        "MNTN"
    ],
    "maniac": [
        "['mey', 'nee', 'ak']",
        "MNK"
    ],
    "manicured": [
        "['man', 'i', 'kyoor', 'd']",
        "MNKRT"
    ],
    "manifest": [
        "[man,uh,fest]",
        "MNFST"
    ],
    "manifested": [
        "[man,uh,fest,ed]",
        "MNFSTT"
    ],
    "manilla": [
        "[muh,nil,uh]",
        "MNL"
    ],
    "mann": [
        "[mahn]",
        "MN"
    ],
    "manners": [
        "['man', 'er', 's']",
        "MNRS"
    ],
    "mannie": [
        "['man', 'ee']",
        "MN"
    ],
    "manning": [
        "['man', 'ing']",
        "MNNK"
    ],
    "mannish": [
        "[man,ish]",
        "MNX"
    ],
    "mans": [
        "['man', 's']",
        "MNS"
    ],
    "mansion": [
        "['man', 'shuhn']",
        "MNSN"
    ],
    "mansions": [
        "['man', 'shuhn', 's']",
        "MNSNS"
    ],
    "manslaughter": [
        "[man,slaw,ter]",
        "MNSLFTR"
    ],
    "manson": [
        "['(mnsn)']",
        "MNSN"
    ],
    "mantle": [
        "['man', 'tl']",
        "MNTL"
    ],
    "manual": [
        "['man', 'yoo', 'uhl']",
        "MNL"
    ],
    "manure": [
        "['muh', 'noor']",
        "MNR"
    ],
    "many": [
        "['men', 'ee']",
        "MN"
    ],
    "map": [
        "['map']",
        "MP"
    ],
    "maple": [
        "['mey', 'puhl']",
        "MPL"
    ],
    "mapped": [
        "[map,ped]",
        "MPT"
    ],
    "maps": [
        "['map', 's']",
        "MPS"
    ],
    "mar": [
        "[mahr]",
        "MR"
    ],
    "maracas": [
        "[muh,rah,kuh,s]",
        "MRKS"
    ],
    "marathon": [
        "['mar', 'uh', 'thon']",
        "MR0N"
    ],
    "marble": [
        "['mahr', 'buhl']",
        "MRPL"
    ],
    "marbles": [
        "[mahr,buhl,s]",
        "MRPLS"
    ],
    "marc": [
        "['mahrk']",
        "MRK"
    ],
    "march": [
        "['mahrch']",
        "MRX"
    ],
    "marching": [
        "[mahrch,ing]",
        "MRXNK"
    ],
    "marcus": [
        "['mahr', 'kuhs']",
        "MRKS"
    ],
    "marcy": [
        "['mahr', 'see']",
        "MRS"
    ],
    "margarita": [
        "['mahr', 'guh', 'ree', 'tuh']",
        "MRKRT"
    ],
    "margaritas": [
        "['mahr', 'guh', 'ree', 'tuh', 's']",
        "MRKRTS"
    ],
    "marge": [
        "['mahrj']",
        "MRJ"
    ],
    "margiela": [
        [
            "mahr",
            "jee",
            "lah"
        ],
        "MRJL"
    ],
    "margin": [
        "[mahr,jin]",
        "MRJN"
    ],
    "maria": [
        "[muh,ree,uh]",
        "MR"
    ],
    "marijuana": [
        "['mar', 'uh', 'wah', 'nuh']",
        "MRJN"
    ],
    "marinate": [
        "['mar', 'uh', 'neyt']",
        "MRNT"
    ],
    "mariner": [
        "[mar,uh,ner]",
        "MRNR"
    ],
    "mark": [
        "['mahrk']",
        "MRK"
    ],
    "marked": [
        "['mahrkt']",
        "MRKT"
    ],
    "markers": [
        "['mahr', 'ker', 's']",
        "MRKRS"
    ],
    "market": [
        "[mahr,kit]",
        "MRKT"
    ],
    "marketed": [
        "[mahr,kit,ed]",
        "MRKTT"
    ],
    "marketing": [
        "[mahr,ki,ting]",
        "MRKTNK"
    ],
    "marking": [
        "[mahr,king]",
        "MRKNK"
    ],
    "marks": [
        "[mahrk,s]",
        "MRKS"
    ],
    "marl": [
        "['mahrl']",
        "MRL"
    ],
    "marley": [
        "['mahr', 'lee']",
        "MRL"
    ],
    "marly": [
        "[mahrl,y]",
        "MRL"
    ],
    "marques": [
        "[mahrk,s]",
        "MRKS"
    ],
    "marriage": [
        "['mar', 'ij']",
        "MRJ"
    ],
    "married": [
        "['mar', 'eed']",
        "MRT"
    ],
    "marrow": [
        "['mar', 'oh']",
        "MR"
    ],
    "marry": [
        "['mar', 'ee']",
        "MR"
    ],
    "mars": [
        "['mahrz']",
        "MRS"
    ],
    "marshall": [
        "['mahr', 'shuhl']",
        "MRXL"
    ],
    "marshmallow": [
        "[mahrsh,mel,oh]",
        "MRXML"
    ],
    "mart": [
        "['mahrt']",
        "MRT"
    ],
    "marta": [
        "['mahr', 'tuh']",
        "MRT"
    ],
    "martian": [
        "['mahr', 'shuhn']",
        "MRXN"
    ],
    "martin": [
        "['mahr', 'tn']",
        "MRTN"
    ],
    "martyr": [
        "['mahr', 'ter']",
        "MRTR"
    ],
    "martyrs": [
        "['mahr', 'ter', 's']",
        "MRTRS"
    ],
    "marvel": [
        "['mahr', 'vuhl']",
        "MRFL"
    ],
    "marvelous": [
        "[mahr,vuh,luhs]",
        "MRFLS"
    ],
    "marvin": [
        "['mahr', 'vin']",
        "MRFN"
    ],
    "mary": [
        "['mair', 'ee']",
        "MR"
    ],
    "maryland": [
        "['mer', 'uh', 'luhnd']",
        "MRLNT"
    ],
    "mas": [
        "['mah', 's']",
        "MS"
    ],
    "mascara": [
        "['ma', 'skar', 'uh']",
        "MSKR"
    ],
    "mascot": [
        "['mas', 'kot']",
        "MSKT"
    ],
    "mash": [
        "[mash]",
        "MX"
    ],
    "mashed": [
        "[masht]",
        "MXT"
    ],
    "mashing": [
        "['mash', 'ing']",
        "MXNK"
    ],
    "mask": [
        "['mask']",
        "MSK"
    ],
    "masked": [
        "[maskt]",
        "MSKT"
    ],
    "masks": [
        "['mask', 's']",
        "MSKS"
    ],
    "mason": [
        "['mey', 'suhn']",
        "MSN"
    ],
    "mass": [
        "[mas]",
        "MS"
    ],
    "massachusetts": [
        "[mas,uh,choo,sits]",
        "MSKSTS"
    ],
    "massacre": [
        "[mas,uh,ker]",
        "MSKR"
    ],
    "massage": [
        "['muh', 'sahzh']",
        "MSJ"
    ],
    "massages": [
        "['muh', 'sahzh', 's']",
        "MSJS"
    ],
    "masses": [
        "[mas,es]",
        "MSS"
    ],
    "massive": [
        "['mas', 'iv']",
        "MSF"
    ],
    "master": [
        "['mas', 'ter']",
        "MSTR"
    ],
    "mastered": [
        "[mas,ter,ed]",
        "MSTRT"
    ],
    "mastermind": [
        "['mas', 'ter', 'mahynd']",
        "MSTRMNT"
    ],
    "masterpiece": [
        "[mas,ter,pees]",
        "MSTRPS"
    ],
    "masters": [
        "['mas', 'terz']",
        "MSTRS"
    ],
    "masturbate": [
        "[mas,ter,beyt]",
        "MSTRPT"
    ],
    "mat": [
        "['mat']",
        "MT"
    ],
    "match": [
        "['mach']",
        "MX"
    ],
    "matchbox": [
        "[mach,boks]",
        "MXPKS"
    ],
    "matches": [
        "[mach,es]",
        "MXS"
    ],
    "matching": [
        "['mach', 'ing']",
        "MXNK"
    ],
    "mate": [
        "[meyt]",
        "MT"
    ],
    "material": [
        "[muh,teer,ee,uhl]",
        "MTRL"
    ],
    "math": [
        "['math']",
        "M0"
    ],
    "mathematician": [
        "['math', 'uh', 'muh', 'tish', 'uhn']",
        "M0MTSN"
    ],
    "mathematics": [
        "['math', 'uh', 'mat', 'iks']",
        "M0MTKS"
    ],
    "matinee": [
        [
            "mah",
            "teen"
        ],
        "MTN"
    ],
    "matrimony": [
        "[ma,truh,moh,nee]",
        "MTRMN"
    ],
    "matrix": [
        "['mey', 'triks']",
        "MTRKS"
    ],
    "mats": [
        "[mats]",
        "MTS"
    ],
    "matt": [
        "['mat']",
        "MT"
    ],
    "matte": [
        "['mat']",
        "MT"
    ],
    "matter": [
        "['mat', 'er']",
        "MTR"
    ],
    "mattered": [
        "['mat', 'er', 'ed']",
        "MTRT"
    ],
    "matters": [
        "[mat,er,s]",
        "MTRS"
    ],
    "matthews": [
        "['math', 'yooz']",
        "M0S"
    ],
    "mattress": [
        "['ma', 'tris']",
        "MTRS"
    ],
    "mattresses": [
        "[ma,tris,es]",
        "MTRSS"
    ],
    "mature": [
        "[muh,toor]",
        "MTR"
    ],
    "maui": [
        "['mou', 'ee']",
        "M"
    ],
    "maury": [
        "['mawr', 'ee']",
        "MR"
    ],
    "maverick": [
        "['mav', 'er', 'ik']",
        "MFRK"
    ],
    "mavericks": [
        "['mav', 'er', 'ik', 's']",
        "MFRKS"
    ],
    "max": [
        "['maks']",
        "MKS"
    ],
    "maxi": [
        "[mak,see]",
        "MKS"
    ],
    "may": [
        "['mey']",
        "M"
    ],
    "mayans": [
        "['mah', 'yuhn', 's']",
        "MNS"
    ],
    "maybe": [
        "['mey', 'bee']",
        "MP"
    ],
    "mayer": [
        "[mahy,eror]",
        "MR"
    ],
    "mayhem": [
        "[mey,hem]",
        "MHM"
    ],
    "mayo": [
        "['mey', 'oh']",
        "M"
    ],
    "mayonnaise": [
        "['mey', 'uh', 'neyz']",
        "MNS"
    ],
    "mayor": [
        "['mey', 'er']",
        "MR"
    ],
    "maze": [
        "[meyz]",
        "MS"
    ],
    "mazi": [
        [
            "maht",
            "see"
        ],
        "MS"
    ],
    "mazzi": [
        [
            "mah",
            "zee"
        ],
        "MS"
    ],
    "mccartney": [
        "['muh', 'kairt', 'nee']",
        "MKRTN"
    ],
    "mcdonalds": [
        [
            "muhk",
            "don",
            "ld"
        ],
        "MKTNLTS"
    ],
    "mcgraw": [
        "['muh', 'graw']",
        "MKR"
    ],
    "mcqueen": [
        [
            "mak",
            "kween"
        ],
        "MKN"
    ],
    "md": [
        "[mnd,lv,m]",
        "MT"
    ],
    "mdma": [
        "[(md,m,)]",
        "MTM"
    ],
    "me": [
        "['mee']",
        "M"
    ],
    "me's": [
        [
            "mees"
        ],
        "MS"
    ],
    "meagan": [
        [
            "meg",
            "uhn"
        ],
        "MKN"
    ],
    "meal": [
        "['meel']",
        "ML"
    ],
    "meals": [
        "['meel', 's']",
        "MLS"
    ],
    "mean": [
        "['meen']",
        "MN"
    ],
    "meaner": [
        "[meen,er]",
        "MNR"
    ],
    "meanest": [
        "[meen,est]",
        "MNST"
    ],
    "meaning": [
        "['mee', 'ning']",
        "MNNK"
    ],
    "means": [
        "['meen', 's']",
        "MNS"
    ],
    "meant": [
        "['ment']",
        "MNT"
    ],
    "meantime": [
        "['meen', 'tahym']",
        "MNTM"
    ],
    "meanwhile": [
        "['meen', 'hwahyl']",
        "MNL"
    ],
    "measure": [
        "[mezh,er]",
        "MSR"
    ],
    "meat": [
        "['meet']",
        "MT"
    ],
    "mecca": [
        "['mek', 'uh']",
        "MK"
    ],
    "mechanics": [
        "['muh', 'kan', 'iks']",
        "MXNKS"
    ],
    "medal": [
        "['med', 'l']",
        "MTL"
    ],
    "medallion": [
        "[muh,dal,yuhn]",
        "MTLN"
    ],
    "medals": [
        "['med', 'l', 's']",
        "MTLS"
    ],
    "media": [
        "['mee', 'dee', 'uh']",
        "MT"
    ],
    "medic": [
        "['med', 'ik']",
        "MTK"
    ],
    "medical": [
        "['med', 'i', 'kuhl']",
        "MTKL"
    ],
    "medication": [
        "['med', 'i', 'key', 'shuhn']",
        "MTKXN"
    ],
    "medicine": [
        "['med', 'uh', 'sinor']",
        "MTSN"
    ],
    "medieval": [
        "['mee', 'dee', 'ee', 'vuhl']",
        "MTFL"
    ],
    "medina": [
        "[muh,dee,nuh]",
        "MTN"
    ],
    "mediocre": [
        "['mee', 'dee', 'oh', 'ker']",
        "MTKR"
    ],
    "meditate": [
        "[med,i,teyt]",
        "MTTT"
    ],
    "meditation": [
        "[med,i,tey,shuhn]",
        "MTTXN"
    ],
    "meds": [
        "['med', 's']",
        "MTS"
    ],
    "medulla": [
        "[muh,duhl,uh]",
        "MTL"
    ],
    "medusa": [
        "['muh', 'doo', 'suh']",
        "MTS"
    ],
    "meek": [
        "['meek']",
        "MK"
    ],
    "meet": [
        "['meet']",
        "MT"
    ],
    "meeting": [
        "['mee', 'ting']",
        "MTNK"
    ],
    "meetings": [
        "[mee,ting,s]",
        "MTNKS"
    ],
    "meets": [
        "[meet,s]",
        "MTS"
    ],
    "megan": [
        "['meg', 'uhn']",
        "MKN"
    ],
    "mel": [
        "['mel']",
        "ML"
    ],
    "melee": [
        "[mey,ley]",
        "ML"
    ],
    "mellow": [
        "['mel', 'oh']",
        "ML"
    ],
    "melodic": [
        "[muh,lod,ik]",
        "MLTK"
    ],
    "melodies": [
        "[mel,uh,dee,s]",
        "MLTS"
    ],
    "melody": [
        "[mel,uh,dee]",
        "MLT"
    ],
    "melon": [
        "[mel,uhn]",
        "MLN"
    ],
    "melt": [
        "['melt']",
        "MLT"
    ],
    "melted": [
        "['melt', 'ed']",
        "MLTT"
    ],
    "melting": [
        "[melt,ing]",
        "MLTNK"
    ],
    "melts": [
        "[melt,s]",
        "MLTS"
    ],
    "member": [
        "['mem', 'ber']",
        "MMPR"
    ],
    "members": [
        "['mem', 'ber', 's']",
        "MMPRS"
    ],
    "membrane": [
        "[mem,breyn]",
        "MMPRN"
    ],
    "memo": [
        "['mem', 'oh']",
        "MM"
    ],
    "memorize": [
        "['mem', 'uh', 'rahyz']",
        "MMRS"
    ],
    "memorized": [
        "['mem', 'uh', 'rahyz', 'd']",
        "MMRST"
    ],
    "memory": [
        "['mem', 'uh', 'ree']",
        "MMR"
    ],
    "memphis": [
        "['mem', 'fis']",
        "MMFS"
    ],
    "men": [
        "['men']",
        "MN"
    ],
    "menace": [
        "['men', 'is']",
        "MNS"
    ],
    "mend": [
        "[mend]",
        "MNT"
    ],
    "menstrual": [
        "['men', 'stroo', 'uhl']",
        "MNSTRL"
    ],
    "mental": [
        "['men', 'tl']",
        "MNTL"
    ],
    "mentality": [
        "[men,tal,i,tee]",
        "MNTLT"
    ],
    "mentally": [
        "['men', 'tl', 'ee']",
        "MNTL"
    ],
    "mention": [
        "['men', 'shuhn']",
        "MNXN"
    ],
    "mentioned": [
        "['men', 'shuhn', 'ed']",
        "MNXNT"
    ],
    "mentioning": [
        "[men,shuhn,ing]",
        "MNXNNK"
    ],
    "mentions": [
        "[men,shuhn,s]",
        "MNXNS"
    ],
    "mentor": [
        "[men,tawr]",
        "MNTR"
    ],
    "menu": [
        "['men', 'yoo']",
        "MN"
    ],
    "mercedes": [
        "['mer', 'se', 'thesfor1mer']",
        "MRSTS"
    ],
    "mercer": [
        "[mur,ser]",
        "MRSR"
    ],
    "merch": [
        "['murch']",
        "MRX"
    ],
    "mercury": [
        "['mur', 'kyuh', 'ree']",
        "MRKR"
    ],
    "mercy": [
        "['mur', 'see']",
        "MRS"
    ],
    "merely": [
        "[meer,lee]",
        "MRL"
    ],
    "merge": [
        "[murj]",
        "MRJ"
    ],
    "merk": [
        "['merk']",
        "MRK"
    ],
    "merlot": [
        "['mur', 'loh']",
        "MRLT"
    ],
    "mermaid": [
        "['mur', 'meyd']",
        "MRMT"
    ],
    "merrily": [
        "[mer,uh,lee]",
        "MRL"
    ],
    "merry": [
        "['mer', 'ee']",
        "MR"
    ],
    "mesmerized": [
        "['mez', 'muh', 'rahyz', 'd']",
        "MSMRST"
    ],
    "mess": [
        "['mes']",
        "MS"
    ],
    "message": [
        "['mes', 'ij']",
        "MSJ"
    ],
    "messages": [
        "[mes,ij,s]",
        "MSJS"
    ],
    "messaging": [
        "['mes', 'uh', 'jing']",
        "MSJNK"
    ],
    "messed": [
        "['mes', 'ed']",
        "MST"
    ],
    "messiah": [
        "['mi', 'sahy', 'uh']",
        "MS"
    ],
    "messing": [
        "['mes', 'ing']",
        "MSNK"
    ],
    "messy": [
        "['mes', 'ee']",
        "MS"
    ],
    "met": [
        "['met']",
        "MT"
    ],
    "metal": [
        "['met', 'l']",
        "MTL"
    ],
    "metaphor": [
        "[met,uh,fawr]",
        "MTFR"
    ],
    "metaphors": [
        "[met,uh,fawr,s]",
        "MTFRS"
    ],
    "meter": [
        "[mee,ter]",
        "MTR"
    ],
    "meters": [
        "[mee,ter,s]",
        "MTRS"
    ],
    "meth": [
        "['meth']",
        "M0"
    ],
    "method": [
        "[meth,uhd]",
        "M0T"
    ],
    "methods": [
        "['meth', 'uhd', 's']",
        "M0TS"
    ],
    "metro": [
        "['me', 'troh']",
        "MTR"
    ],
    "metropolis": [
        "[mi,trop,uh,lis]",
        "MTRPLS"
    ],
    "mexican": [
        "['mek', 'si', 'kuhn']",
        "MKSKN"
    ],
    "mexicano": [
        "['me', 'hee', 'kah', 'noh']",
        "MKSKN"
    ],
    "mexicans": [
        "['mek', 'si', 'kuhn', 's']",
        "MKSKNS"
    ],
    "mexico": [
        "['mek', 'si', 'koh']",
        "MKSK"
    ],
    "mg": [
        "['mg', 'nz', 'm']",
        "MK"
    ],
    "mi": [
        "['mee']",
        "M"
    ],
    "miami": [
        "['mahy', 'am', 'ee']",
        "MM"
    ],
    "mic": [
        "['mahyk']",
        "MK"
    ],
    "mic's": [
        "[mahyk,'s]",
        "MKKS"
    ],
    "mice": [
        "['mahys']",
        "MS"
    ],
    "michael": [
        "['mahy', 'kuhl']",
        "MKL"
    ],
    "michelin": [
        [
            "mich",
            "lin"
        ],
        "MXLN"
    ],
    "michigan": [
        "[mish,i,guhn]",
        "MXKN"
    ],
    "mick": [
        "['mik']",
        "MK"
    ],
    "mickey": [
        "['mik', 'ee']",
        "MK"
    ],
    "micky": [
        "['mik', 'ee']",
        "MK"
    ],
    "microphone": [
        "['mahy', 'kruh', 'fohn']",
        "MKRFN"
    ],
    "microwave": [
        "['mahy', 'kroh', 'weyv']",
        "MKRF"
    ],
    "mics": [
        "['mahyk', 's']",
        "MKS"
    ],
    "mid": [
        "['mid']",
        "MT"
    ],
    "midas": [
        "['mahy', 'duhs']",
        "MTS"
    ],
    "middle": [
        "['mid', 'l']",
        "MTL"
    ],
    "middleman": [
        "['mid', 'l', 'man']",
        "MTLMN"
    ],
    "midget": [
        "['mij', 'it']",
        "MJT"
    ],
    "midgets": [
        "['mij', 'it', 's']",
        "MJTS"
    ],
    "midnight": [
        "['mid', 'nahyt']",
        "MTNT"
    ],
    "midst": [
        "[midst]",
        "MTST"
    ],
    "midwest": [
        "[mid,west]",
        "MTST"
    ],
    "might": [
        "['mahyt']",
        "MT"
    ],
    "mighty": [
        "['mahy', 'tee']",
        "MT"
    ],
    "mike": [
        "['mahyk']",
        "MK"
    ],
    "mike's": [
        "[mahyk,'s]",
        "MKS"
    ],
    "mikes": [
        "[mahyk,s]",
        "MKS"
    ],
    "mil": [
        "['mil']",
        "ML"
    ],
    "milan": [
        "[mi,lan]",
        "MLN"
    ],
    "mild": [
        "[mahyld]",
        "MLT"
    ],
    "mile": [
        "['mahyl']",
        "ML"
    ],
    "mileage": [
        "['mahy', 'lij']",
        "MLJ"
    ],
    "miles": [
        "['mahylz']",
        "MLS"
    ],
    "milf": [
        "['milf']",
        "MLF"
    ],
    "military": [
        "['mil', 'i', 'ter', 'ee']",
        "MLTR"
    ],
    "militia": [
        "['mi', 'lish', 'uh']",
        "MLX"
    ],
    "milk": [
        "['milk']",
        "MLK"
    ],
    "milked": [
        "[milk,ed]",
        "MLKT"
    ],
    "milky": [
        "['mil', 'kee']",
        "MLK"
    ],
    "mill": [
        "['mil']",
        "ML"
    ],
    "millennium": [
        "['mi', 'len', 'ee', 'uhm']",
        "MLNM"
    ],
    "miller": [
        "['mil', 'er']",
        "MLR"
    ],
    "millers": [
        "[mil,er,s]",
        "MLRS"
    ],
    "millimeter": [
        "[mil,uh,mee,ter]",
        "MLMTR"
    ],
    "millimeters": [
        "[mil,uh,mee,ter,s]",
        "MLMTRS"
    ],
    "million": [
        "['mil', 'yuhn']",
        "MLN"
    ],
    "millionaire": [
        "['mil', 'yuh', 'nair']",
        "MLNR"
    ],
    "millionaires": [
        "[mil,yuh,nair,s]",
        "MLNRS"
    ],
    "millions": [
        "['mil', 'yuhn', 's']",
        "MLNS"
    ],
    "millis": [
        [
            "mil",
            "iz"
        ],
        "MLS"
    ],
    "mills": [
        "['milz']",
        "MLS"
    ],
    "milly": [
        "['mil', 'ee']",
        "ML"
    ],
    "mils": [
        "['mil', 's']",
        "MLS"
    ],
    "mimi": [
        "[mee,mee]",
        "MM"
    ],
    "mimic": [
        "[mim,ik]",
        "MMK"
    ],
    "mimicking": [
        "[mim,ik,king]",
        "MMKNK"
    ],
    "mimosa": [
        "[mi,moh,suh]",
        "MMS"
    ],
    "mind": [
        "['mahynd']",
        "MNT"
    ],
    "mind's": [
        "['mahynd', \"'s\"]",
        "MNTTS"
    ],
    "minded": [
        "['mahyn', 'did']",
        "MNTT"
    ],
    "minding": [
        "[mahynd,ing]",
        "MNTNK"
    ],
    "minds": [
        "['mahynd', 's']",
        "MNTS"
    ],
    "mine": [
        "['mahyn']",
        "MN"
    ],
    "mine's": [
        "['mahyn', \"'s\"]",
        "MNS"
    ],
    "mines": [
        "['mahyn', 's']",
        "MNS"
    ],
    "ming": [
        "['ming']",
        "MNK"
    ],
    "mingle": [
        "['ming', 'guhl']",
        "MNKL"
    ],
    "mini": [
        "['min', 'ee']",
        "MN"
    ],
    "minimal": [
        "['min', 'uh', 'muhl']",
        "MNML"
    ],
    "minimum": [
        "[min,uh,muhm]",
        "MNMM"
    ],
    "minister": [
        "['min', 'uh', 'ster']",
        "MNSTR"
    ],
    "minivan": [
        "[min,ee,van]",
        "MNFN"
    ],
    "minivans": [
        "[min,ee,van,s]",
        "MNFNS"
    ],
    "mink": [
        "['mingk']",
        "MNK"
    ],
    "minks": [
        "['mingk', 's']",
        "MNKS"
    ],
    "minnesota": [
        "['min', 'uh', 'soh', 'tuh']",
        "MNST"
    ],
    "minor": [
        "['mahy', 'ner']",
        "MNR"
    ],
    "minority": [
        "[mi,nawr,i,tee]",
        "MNRT"
    ],
    "minors": [
        "[mahy,ner,s]",
        "MNRS"
    ],
    "mint": [
        "['mint']",
        "MNT"
    ],
    "minus": [
        "['mahy', 'nuhs']",
        "MNS"
    ],
    "minute": [
        "['min', 'it']",
        "MNT"
    ],
    "minutes": [
        "['min', 'it', 's']",
        "MNTS"
    ],
    "miny": [
        [
            "mah",
            "nee"
        ],
        "MN"
    ],
    "miracle": [
        "['mir', 'uh', 'kuhl']",
        "MRKL"
    ],
    "miracles": [
        "['mir', 'uh', 'kuhl', 's']",
        "MRKLS"
    ],
    "mirage": [
        "[mi,rahzh]",
        "MRJ"
    ],
    "mirror": [
        "['mir', 'er']",
        "MRR"
    ],
    "mirrors": [
        "['mir', 'er', 's']",
        "MRRS"
    ],
    "mis": [
        "[mee]",
        "MS"
    ],
    "miscellaneous": [
        "[mis,uh,ley,nee,uhs]",
        "MSLNS"
    ],
    "misdemeanor": [
        "[mis,di,mee,ner]",
        "MSTMNR"
    ],
    "miserable": [
        "[miz,er,uh,buhl]",
        "MSRPL"
    ],
    "misery": [
        "[miz,uh,ree]",
        "MSR"
    ],
    "misfit": [
        "[mis,fitfor1mis]",
        "MSFT"
    ],
    "misfits": [
        "['mis', 'fitfor1mis', 's']",
        "MSFTS"
    ],
    "mislead": [
        "['mis', 'leed']",
        "MLT"
    ],
    "misprint": [
        "[nounmis,print]",
        "MSPRNT"
    ],
    "miss": [
        "['mis']",
        "MS"
    ],
    "missed": [
        "['mis', 'ed']",
        "MST"
    ],
    "misses": [
        "['mis', 'es']",
        "MSS"
    ],
    "missile": [
        "['mis', 'uhlor']",
        "MSL"
    ],
    "missiles": [
        "['mis', 'uhlor', 's']",
        "MSLS"
    ],
    "missing": [
        "['mis', 'ing']",
        "MSNK"
    ],
    "mission": [
        "['mish', 'uhn']",
        "MSN"
    ],
    "missionary": [
        "[mish,uh,ner,ee]",
        "MSNR"
    ],
    "missions": [
        "['mish', 'uhn', 's']",
        "MSNS"
    ],
    "mississippi": [
        "[mis,uh,sip,ee]",
        "MSSP"
    ],
    "missouri": [
        "[mi,zoor,ee]",
        "MSR"
    ],
    "missus": [
        "['mis', 'uhz']",
        "MSS"
    ],
    "missy": [
        "[mis,ee]",
        "MS"
    ],
    "mist": [
        "['mist']",
        "MST"
    ],
    "mistake": [
        "['mi', 'steyk']",
        "MSTK"
    ],
    "mistaken": [
        "[mi,stey,kuhn]",
        "MSTKN"
    ],
    "mistakes": [
        "['mi', 'steyk', 's']",
        "MSTKS"
    ],
    "mister": [
        "['mis', 'ter']",
        "MSTR"
    ],
    "mistletoe": [
        "['mis', 'uhl', 'toh']",
        "MSTLT"
    ],
    "mistreat": [
        "['mis', 'treet']",
        "MSTRT"
    ],
    "mistress": [
        "['mis', 'tris']",
        "MSTRS"
    ],
    "misunderstanding": [
        "['mis', 'uhn', 'der', 'stan', 'ding']",
        "MSNTRSTNTNK"
    ],
    "misunderstood": [
        "['mis', 'uhn', 'der', 'stood']",
        "MSNTRSTT"
    ],
    "mitchell": [
        "['mich', 'uhl']",
        "MXL"
    ],
    "mite": [
        "['mahyt']",
        "MT"
    ],
    "mittens": [
        "[mit,n,s]",
        "MTNS"
    ],
    "mitzvah": [
        "['SephardicHebrewmeets', 'vah']",
        "MTSF"
    ],
    "mitzvahs": [
        "[SephardicHebrewmeets,vah,s]",
        "MTSFS"
    ],
    "mix": [
        "['miks']",
        "MKS"
    ],
    "mixed": [
        "['mikst']",
        "MKST"
    ],
    "mixes": [
        "['miks', 'es']",
        "MKSS"
    ],
    "mixing": [
        "['miks', 'ing']",
        "MKSNK"
    ],
    "mixtape": [
        "['miks', 'teyp']",
        "MKSTP"
    ],
    "mixtapes": [
        "['miks', 'teyp', 's']",
        "MKSTPS"
    ],
    "mixture": [
        "[miks,cher]",
        "MKSTR"
    ],
    "mj": [
        [
            "em",
            "jey"
        ],
        "MJ"
    ],
    "mo": [
        "['moh']",
        "M"
    ],
    "moan": [
        "['mohn']",
        "MN"
    ],
    "moaning": [
        "['mohn', 'ing']",
        "MNNK"
    ],
    "moat": [
        "[moht]",
        "MT"
    ],
    "mob": [
        "['mob']",
        "MP"
    ],
    "mobbing": [
        "['mob', 'bing']",
        "MPNK"
    ],
    "mobile": [
        "['moh', 'buhl']",
        "MPL"
    ],
    "mobster": [
        "['mob', 'ster']",
        "MPSTR"
    ],
    "mobsters": [
        "['mob', 'ster', 's']",
        "MPSTRS"
    ],
    "mocking": [
        "[mok,ing]",
        "MKNK"
    ],
    "mode": [
        "['mohd']",
        "MT"
    ],
    "model": [
        "['mod', 'l']",
        "MTL"
    ],
    "modeling": [
        "[mod,l,ing]",
        "MTLNK"
    ],
    "modelling": [
        "[mod,l,ling]",
        "MTLNK"
    ],
    "models": [
        "['mod', 'l', 's']",
        "MTLS"
    ],
    "modern": [
        "['mod', 'ern']",
        "MTRN"
    ],
    "modest": [
        "['mod', 'ist']",
        "MTST"
    ],
    "moe": [
        "['moh']",
        "M"
    ],
    "mogul": [
        "['moh', 'guhl']",
        "MKL"
    ],
    "moist": [
        "['moist']",
        "MST"
    ],
    "mojo": [
        "['moh', 'joh']",
        "MJ"
    ],
    "mold": [
        "['mohld']",
        "MLT"
    ],
    "molded": [
        "['mohld', 'ed']",
        "MLTT"
    ],
    "molest": [
        "['muh', 'lest']",
        "MLST"
    ],
    "mollies": [
        "['mol', 'ee', 's']",
        "MLS"
    ],
    "molly": [
        "['mol', 'ee']",
        "ML"
    ],
    "molly's": [
        "['mol', 'ee', \"'s\"]",
        "MLS"
    ],
    "mollys": [
        "['mol', 'ee', 's']",
        "MLS"
    ],
    "molotov": [
        "['mol', 'uh', 'tawf']",
        "MLTF"
    ],
    "mom": [
        "['mom']",
        "MM"
    ],
    "mom's": [
        "['mom', \"'s\"]",
        "MMMS"
    ],
    "moment": [
        "['moh', 'muhnt']",
        "MMNT"
    ],
    "momentarily": [
        "['moh', 'muhn', 'tair', 'uh', 'lee']",
        "MMNTRL"
    ],
    "moments": [
        "['moh', 'muhnt', 's']",
        "MMNTS"
    ],
    "momma": [
        "['mom', 'uh']",
        "MM"
    ],
    "momma's": [
        "['mom', 'uh', \"'s\"]",
        "MMS"
    ],
    "mommas": [
        "['mom', 'uh', 's']",
        "MMS"
    ],
    "mommy's": [
        "['mom', 'ee', \"'s\"]",
        "MMS"
    ],
    "moms": [
        "['mom', 's']",
        "MMS"
    ],
    "mon": [
        "[mon]",
        "MN"
    ],
    "mona": [
        "['moh', 'nuh']",
        "MN"
    ],
    "monday": [
        "['muhn', 'dey']",
        "MNT"
    ],
    "money": [
        "['muhn', 'ee']",
        "MN"
    ],
    "money's": [
        "['muhn', 'ee', \"'s\"]",
        "MNS"
    ],
    "monica": [
        "['mon', 'i', 'kuh']",
        "MNK"
    ],
    "monique": [
        [
            "muh",
            "neek"
        ],
        "MNK"
    ],
    "monitor": [
        "[mon,i,ter]",
        "MNTR"
    ],
    "monk": [
        "[muhngk]",
        "MNK"
    ],
    "monkey": [
        "['muhng', 'kee']",
        "MNK"
    ],
    "monkeys": [
        "[muhng,kee,s]",
        "MNKS"
    ],
    "monogamous": [
        "[muh,nog,uh,muhs]",
        "MNKMS"
    ],
    "monopoly": [
        "['muh', 'nop', 'uh', 'lee']",
        "MNPL"
    ],
    "monotone": [
        "[mon,uh,tohn]",
        "MNTN"
    ],
    "monroe": [
        "[muhn,roh]",
        "MNR"
    ],
    "monsoon": [
        "['mon', 'soon']",
        "MNSN"
    ],
    "monster": [
        "['mon', 'ster']",
        "MNSTR"
    ],
    "monster's": [
        "[mon,ster,'s]",
        "MNSTRRS"
    ],
    "monsters": [
        "['mon', 'ster', 's']",
        "MNSTRS"
    ],
    "monte": [
        "[mon,tee]",
        "MNT"
    ],
    "month": [
        "['muhnth']",
        "MN0"
    ],
    "months": [
        "['muhnth', 's']",
        "MN0S"
    ],
    "monumental": [
        "[mon,yuh,men,tl]",
        "MNMNTL"
    ],
    "moo": [
        "[moo]",
        "M"
    ],
    "mood": [
        "['mood']",
        "MT"
    ],
    "moods": [
        "[mood,s]",
        "MTS"
    ],
    "moolah": [
        "['moo', 'luh', 'h']",
        "ML"
    ],
    "moon": [
        "['moon']",
        "MN"
    ],
    "moonlight": [
        "[moon,lahyt]",
        "MNLT"
    ],
    "moonshine": [
        "[moon,shahyn]",
        "MNXN"
    ],
    "moonwalk": [
        "['moon', 'wawk']",
        "MNLK"
    ],
    "moonwalking": [
        "['moon', 'wawk', 'ing']",
        "MNLKNK"
    ],
    "moore": [
        "[moor]",
        "MR"
    ],
    "mop": [
        "['mop']",
        "MP"
    ],
    "mope": [
        "[mohp]",
        "MP"
    ],
    "mopping": [
        "[mop,ping]",
        "MPNK"
    ],
    "moral": [
        "[mawr,uhl]",
        "MRL"
    ],
    "morals": [
        "['mawr', 'uhl', 's']",
        "MRLS"
    ],
    "more": [
        "['mawr']",
        "MR"
    ],
    "morgue": [
        "['mawrg']",
        "MRK"
    ],
    "morn": [
        "[mawrn]",
        "MRN"
    ],
    "morning": [
        "['mawr', 'ning']",
        "MRNNK"
    ],
    "moron": [
        "['mawr', 'on']",
        "MRN"
    ],
    "morphine": [
        "['mawr', 'feen']",
        "MRFN"
    ],
    "morphing": [
        "[mawr,fing]",
        "MRFNK"
    ],
    "mortal": [
        "['mawr', 'tl']",
        "MRTL"
    ],
    "mortgage": [
        "['mawr', 'gij']",
        "MRTKJ"
    ],
    "mos": [
        "[moh]",
        "MS"
    ],
    "moses": [
        "['moh', 'ziz']",
        "MSS"
    ],
    "mosh": [
        "['mosh']",
        "MX"
    ],
    "mosquito": [
        "[muh,skee,toh]",
        "MSKT"
    ],
    "moss": [
        "[maws]",
        "MS"
    ],
    "most": [
        "['mohst']",
        "MST"
    ],
    "mostly": [
        "['mohst', 'lee']",
        "MSTL"
    ],
    "motel": [
        "[moh,tel]",
        "MTL"
    ],
    "motels": [
        "[moh,tel,s]",
        "MTLS"
    ],
    "moth": [
        "[mawth]",
        "M0"
    ],
    "mother": [
        "['muhth', 'er']",
        "M0R"
    ],
    "mother's": [
        "['muhth', 'er', \"'s\"]",
        "M0RRS"
    ],
    "motherfucker": [
        "['muhth', 'er', 'fuhk', 'er']",
        "M0RFKR"
    ],
    "motherfuckers": [
        "['muhth', 'er', 'fuhk', 'er', 's']",
        "M0RFKRS"
    ],
    "mothers": [
        "['muhth', 'er', 's']",
        "M0RS"
    ],
    "motion": [
        "['moh', 'shuhn']",
        "MXN"
    ],
    "motionless": [
        "[moh,shuhn,lis]",
        "MXNLS"
    ],
    "motions": [
        "['moh', 'shuhn', 's']",
        "MXNS"
    ],
    "motivate": [
        "['moh', 'tuh', 'veyt']",
        "MTFT"
    ],
    "motivated": [
        "[moh,tuh,veyt,d]",
        "MTFTT"
    ],
    "motivation": [
        "['moh', 'tuh', 'vey', 'shuhn']",
        "MTFXN"
    ],
    "motivational": [
        "[moh,tuh,vey,shuhn,al]",
        "MTFXNL"
    ],
    "motive": [
        "['moh', 'tiv']",
        "MTF"
    ],
    "motives": [
        "[moh,tiv,s]",
        "MTFS"
    ],
    "motor": [
        "['moh', 'ter']",
        "MTR"
    ],
    "motorcycle": [
        "['moh', 'ter', 'sahy', 'kuhl']",
        "MTRSKL"
    ],
    "motors": [
        "[moh,ter,s]",
        "MTRS"
    ],
    "motown": [
        "[moh,toun]",
        "MTN"
    ],
    "motto": [
        "['mot', 'oh']",
        "MT"
    ],
    "mound": [
        "[mound]",
        "MNT"
    ],
    "mount": [
        "['mount']",
        "MNT"
    ],
    "mountain": [
        "['moun', 'tn']",
        "MNTN"
    ],
    "mountains": [
        "['moun', 'tn', 's']",
        "MNTNS"
    ],
    "mounted": [
        "[moun,tid]",
        "MNTT"
    ],
    "mourn": [
        "[mawrn]",
        "MRN"
    ],
    "mourning": [
        "[mawr,ning]",
        "MRNNK"
    ],
    "mouse": [
        "['nounmous']",
        "MS"
    ],
    "mouses": [
        "[nounmous,s]",
        "MSS"
    ],
    "mouth": [
        "['nounmouth']",
        "M0"
    ],
    "mouthpiece": [
        "[mouth,pees]",
        "M0PS"
    ],
    "mouths": [
        "['nounmouth', 's']",
        "M0S"
    ],
    "move": [
        "['moov']",
        "MF"
    ],
    "moved": [
        "['moov', 'd']",
        "MFT"
    ],
    "movement": [
        "['moov', 'muhnt']",
        "MFMNT"
    ],
    "mover": [
        "['moo', 'ver']",
        "MFR"
    ],
    "moves": [
        "['moov', 's']",
        "MFS"
    ],
    "movie": [
        "['moo', 'vee']",
        "MF"
    ],
    "movies": [
        "['moo', 'vee', 's']",
        "MFS"
    ],
    "moving": [
        "['moo', 'ving']",
        "MFNK"
    ],
    "mow": [
        "[moh]",
        "M"
    ],
    "mower": [
        "['moh', 'er']",
        "MR"
    ],
    "mozart": [
        "['moht', 'sahrt']",
        "MSRT"
    ],
    "mr": [
        "['mis', 'ter']",
        "MR"
    ],
    "mrs": [
        "['mis', 'iz', '']",
        "MRS"
    ],
    "ms": [
        "['em']",
        "MS"
    ],
    "mu": [
        "['myoo']",
        "M"
    ],
    "much": [
        "['muhch']",
        "MX"
    ],
    "mud": [
        "['muhd']",
        "MT"
    ],
    "muddy": [
        "['muhd', 'ee']",
        "MT"
    ],
    "muffing": [
        "[muhf,ing]",
        "MFNK"
    ],
    "muffins": [
        "[muhf,in,s]",
        "MFNS"
    ],
    "muffler": [
        "[muhf,ler]",
        "MFLR"
    ],
    "mufflers": [
        "[muhf,ler,s]",
        "MFLRS"
    ],
    "mug": [
        "['muhg']",
        "MK"
    ],
    "mugging": [
        "['muhg', 'ing']",
        "MKNK"
    ],
    "mugs": [
        "[muhg,s]",
        "MKS"
    ],
    "muhammad": [
        "[moo,ham,uhd]",
        "MHMT"
    ],
    "mule": [
        "[myool]",
        "ML"
    ],
    "mullah": [
        "[muhl,uh]",
        "ML"
    ],
    "muller": [
        "['muhl', 'er']",
        "MLR"
    ],
    "multi": [
        "['muhl', 'tee']",
        "MLT"
    ],
    "multiple": [
        "[muhl,tuh,puhl]",
        "MLTPL"
    ],
    "multiply": [
        "['muhl', 'tuh', 'plahy']",
        "MLTPL"
    ],
    "mumble": [
        "[muhm,buhl]",
        "MMPL"
    ],
    "mummy": [
        "['muhm', 'ee']",
        "MM"
    ],
    "munch": [
        "['muhnch']",
        "MNX"
    ],
    "munching": [
        "[muhnch,ing]",
        "MNXNK"
    ],
    "mural": [
        "[myoor,uhl]",
        "MRL"
    ],
    "murder": [
        "['mur', 'der']",
        "MRTR"
    ],
    "murdered": [
        "['mur', 'der', 'ed']",
        "MRTRT"
    ],
    "murderer": [
        "['mur', 'der', 'er']",
        "MRTRR"
    ],
    "murderers": [
        "['mur', 'der', 'er', 's']",
        "MRTRRS"
    ],
    "murdering": [
        "['mur', 'der', 'ing']",
        "MRTRNK"
    ],
    "murderous": [
        "[mur,der,uhs]",
        "MRTRS"
    ],
    "murders": [
        "['mur', 'der', 's']",
        "MRTRS"
    ],
    "murk": [
        "['murk']",
        "MRK"
    ],
    "murky": [
        "[mur,kee]",
        "MRK"
    ],
    "murphy": [
        "[mur,fee]",
        "MRF"
    ],
    "muscle": [
        "['muhs', 'uhl']",
        "MSK"
    ],
    "muscles": [
        "[muhs,uhl,s]",
        "MSKS"
    ],
    "museum": [
        "[myoo,zee,uhm]",
        "MSM"
    ],
    "mushroom": [
        "[muhsh,room]",
        "MXRM"
    ],
    "mushrooms": [
        "['muhsh', 'room', 's']",
        "MXRMS"
    ],
    "music": [
        "['myoo', 'zik']",
        "MSK"
    ],
    "music's": [
        "['myoo', 'zik', \"'s\"]",
        "MSKKS"
    ],
    "musical": [
        "[myoo,zi,kuhl]",
        "MSKL"
    ],
    "musician": [
        "[myoo,zish,uhn]",
        "MSSN"
    ],
    "musk": [
        "['muhsk']",
        "MSK"
    ],
    "muslim": [
        "[muhz,lim]",
        "MSLM"
    ],
    "muslims": [
        "[muhz,lim,s]",
        "MSLMS"
    ],
    "must": [
        "['muhst']",
        "MST"
    ],
    "mustache": [
        "[muhs,tash]",
        "MSTX"
    ],
    "mustang": [
        "['muhs', 'tang']",
        "MSTNK"
    ],
    "mustard": [
        "['muhs', 'terd']",
        "MSTRT"
    ],
    "musty": [
        "['muhs', 'tee']",
        "MST"
    ],
    "mutant": [
        "[myoot,nt]",
        "MTNT"
    ],
    "mute": [
        "['myoot']",
        "MT"
    ],
    "mutombo": [
        [
            "moo",
            "tohm",
            "boh"
        ],
        "MTMP"
    ],
    "mutt": [
        "['muht']",
        "MT"
    ],
    "mutual": [
        "['myoo', 'choo', 'uhl']",
        "MTL"
    ],
    "muzzle": [
        "[muhz,uhl]",
        "MSL"
    ],
    "mvp": [
        [
            "em",
            "vee",
            "pee"
        ],
        "MFP"
    ],
    "my": [
        "['mahy']",
        "M"
    ],
    "myers": [
        [
            "mahy",
            "urs"
        ],
        "MRS"
    ],
    "myrtle": [
        "[mur,tl]",
        "MRTL"
    ],
    "myself": [
        "['mahy', 'self']",
        "MSLF"
    ],
    "mystery": [
        "['mis', 'tuh', 'ree']",
        "MSTR"
    ],
    "myth": [
        "[mith]",
        "M0"
    ],
    "m\u00e9nage": [
        "['mey', 'nahzh']",
        "MNJ"
    ],
    "n": [
        "['en', '']",
        "N"
    ],
    "na": [
        "['nah']",
        "N"
    ],
    "nab": [
        "['nab']",
        "NP"
    ],
    "nacho": [
        "['nah', 'choh']",
        "NK"
    ],
    "nada": [
        "[nah,duh]",
        "NT"
    ],
    "nae": [
        "['ney']",
        "N"
    ],
    "nag": [
        "[nag]",
        "NK"
    ],
    "nagging": [
        "['nag', 'ing']",
        "NJNK"
    ],
    "nah": [
        "['na']",
        "N"
    ],
    "nail": [
        "['neyl']",
        "NL"
    ],
    "nails": [
        "['neyl', 's']",
        "NLS"
    ],
    "naive": [
        "[nah,eev]",
        "NF"
    ],
    "naked": [
        "['ney', 'kid']",
        "NKT"
    ],
    "name": [
        "['neym']",
        "NM"
    ],
    "name's": [
        "['neym', \"'s\"]",
        "NMS"
    ],
    "named": [
        "['neym', 'd']",
        "NMT"
    ],
    "nameless": [
        "['neym', 'lis']",
        "NMLS"
    ],
    "names": [
        "['neym', 's']",
        "NMS"
    ],
    "naming": [
        [
            "nah",
            "ming"
        ],
        "NMNK"
    ],
    "nan": [
        "[nahn]",
        "NN"
    ],
    "nana": [
        "['nan', 'uh']",
        "NN"
    ],
    "nancy": [
        "[nan,see]",
        "NNS"
    ],
    "nanna": [
        "[nahn,nah]",
        "NN"
    ],
    "nanny": [
        "['nan', 'ee']",
        "NN"
    ],
    "naomi": [
        "[ney,oh,mee]",
        "NM"
    ],
    "nap": [
        "['nap']",
        "NP"
    ],
    "napkin": [
        "[nap,kin]",
        "NPKN"
    ],
    "napkins": [
        "['nap', 'kin', 's']",
        "NPKNS"
    ],
    "napping": [
        "[nap,ping]",
        "NPNK"
    ],
    "nappy": [
        "['nap', 'ee']",
        "NP"
    ],
    "naps": [
        "[nap,s]",
        "NPS"
    ],
    "narc": [
        "['nahrk']",
        "NRK"
    ],
    "narcissists": [
        "['nahr', 'suh', 'sist', 's']",
        "NRSSSTS"
    ],
    "narcotics": [
        "['nahr', 'kot', 'ik', 's']",
        "NRKTKS"
    ],
    "narcs": [
        "['nahrk', 's']",
        "NRKS"
    ],
    "narrative": [
        "[nar,uh,tiv]",
        "NRTF"
    ],
    "nasa": [
        "['nas', 'uh']",
        "NS"
    ],
    "nascar": [
        "['nas', 'kahr']",
        "NSKR"
    ],
    "nasdaq": [
        "[nas,dak]",
        "NSTK"
    ],
    "nash": [
        "[nash]",
        "NX"
    ],
    "nast": [
        "['nast']",
        "NST"
    ],
    "nasty": [
        "['nas', 'tee']",
        "NST"
    ],
    "nat": [
        "['nat']",
        "NT"
    ],
    "nation": [
        "['ney', 'shuhn']",
        "NXN"
    ],
    "national": [
        "[nash,uh,nl]",
        "NXNL"
    ],
    "nations": [
        "['ney', 'shuhn', 's']",
        "NXNS"
    ],
    "natives": [
        "[ney,tiv,s]",
        "NTFS"
    ],
    "natural": [
        "['nach', 'er', 'uhl']",
        "NTRL"
    ],
    "nature": [
        "['ney', 'cher']",
        "NTR"
    ],
    "naughty": [
        "['naw', 'tee']",
        "NKT"
    ],
    "nauseous": [
        "['naw', 'shuhs']",
        "NSS"
    ],
    "naval": [
        "['ney', 'vuhl']",
        "NFL"
    ],
    "navel": [
        "[ney,vuhl]",
        "NFL"
    ],
    "navigate": [
        "[nav,i,geyt]",
        "NFKT"
    ],
    "navigated": [
        "[nav,i,geyt,d]",
        "NFKTT"
    ],
    "navigation": [
        "[nav,i,gey,shuhn]",
        "NFKXN"
    ],
    "navigator": [
        "[nav,i,gey,ter]",
        "NFKTR"
    ],
    "navy": [
        "['ney', 'vee']",
        "NF"
    ],
    "nay": [
        "['ney']",
        "N"
    ],
    "nazi": [
        "['naht', 'see']",
        "NS"
    ],
    "nazis": [
        "[naht,see,s]",
        "NSS"
    ],
    "nd": [
        "[n,dm,m]",
        "NT"
    ],
    "ne": [
        "[neepluhsuhl,truh]",
        "N"
    ],
    "near": [
        "['neer']",
        "NR"
    ],
    "nearer": [
        "[neer,er]",
        "NRR"
    ],
    "nearest": [
        "[neer,est]",
        "NRST"
    ],
    "nearly": [
        "[neer,lee]",
        "NRL"
    ],
    "neat": [
        "['neet']",
        "NT"
    ],
    "necessary": [
        "['nes', 'uh', 'ser', 'ee']",
        "NSSR"
    ],
    "necessity": [
        "[nuh,ses,i,tee]",
        "NSST"
    ],
    "neck": [
        "['nek']",
        "NK"
    ],
    "necklace": [
        "['nek', 'lis']",
        "NKLS"
    ],
    "necklaces": [
        "[nek,lis,s]",
        "NKLSS"
    ],
    "necks": [
        "[nek,s]",
        "NKS"
    ],
    "need": [
        "['need']",
        "NT"
    ],
    "needed": [
        "['nee', 'did']",
        "NTT"
    ],
    "needer": [
        "['need', 'er']",
        "NTR"
    ],
    "needing": [
        "['need', 'ing']",
        "NTNK"
    ],
    "needle": [
        "['need', 'l']",
        "NTL"
    ],
    "needles": [
        "['need', 'lz']",
        "NTLS"
    ],
    "needs": [
        "['needz']",
        "NTS"
    ],
    "needy": [
        "[nee,dee]",
        "NT"
    ],
    "negative": [
        "['neg', 'uh', 'tiv']",
        "NKTF"
    ],
    "negatives": [
        "[neg,uh,tiv,s]",
        "NKTFS"
    ],
    "neglect": [
        "[ni,glekt]",
        "NKLKT"
    ],
    "neglected": [
        "['ni', 'glekt', 'ed']",
        "NKLKTT"
    ],
    "neglecting": [
        "[ni,glekt,ing]",
        "NKLKTNK"
    ],
    "negro": [
        "['nee', 'groh']",
        "NKR"
    ],
    "neighbor": [
        "['ney', 'ber']",
        "NPR"
    ],
    "neighbor's": [
        "['ney', 'ber', \"'s\"]",
        "NPRRS"
    ],
    "neighborhood": [
        "['ney', 'ber', 'hood']",
        "NPRT"
    ],
    "neighbors": [
        "['ney', 'ber', 's']",
        "NPRS"
    ],
    "neither": [
        "['nee', 'ther']",
        "N0R"
    ],
    "nelly": [
        "['nel', 'ee']",
        "NL"
    ],
    "nemo": [
        "['nee', 'moh']",
        "NM"
    ],
    "neon": [
        "['nee', 'on']",
        "NN"
    ],
    "nephew": [
        "['nef', 'yooor']",
        "NF"
    ],
    "nephews": [
        "[nef,yooor,s]",
        "NFS"
    ],
    "neptune": [
        "['nep', 'toon']",
        "NPTN"
    ],
    "neptunes": [
        "[nep,toon,s]",
        "NPTNS"
    ],
    "nerd": [
        "['nurd']",
        "NRT"
    ],
    "nerds": [
        "['nurd', 's']",
        "NRTS"
    ],
    "nerdy": [
        "['nur', 'dee']",
        "NRT"
    ],
    "nero": [
        "[neer,oh]",
        "NR"
    ],
    "nerve": [
        "['nurv']",
        "NRF"
    ],
    "nerves": [
        "['nurv', 's']",
        "NRFS"
    ],
    "nervous": [
        "['nur', 'vuhs']",
        "NRFS"
    ],
    "ness": [
        "['nes']",
        "NS"
    ],
    "nest": [
        "[nest]",
        "NST"
    ],
    "net": [
        "['net']",
        "NT"
    ],
    "nets": [
        "[net,s]",
        "NTS"
    ],
    "network": [
        "['net', 'wurk']",
        "NTRK"
    ],
    "neutral": [
        "['noo', 'truhl']",
        "NTRL"
    ],
    "neva": [
        "['nee', 'vuh']",
        "NF"
    ],
    "nevada": [
        "['nuh', 'vad', 'uh']",
        "NFT"
    ],
    "never": [
        "['nev', 'er']",
        "NFR"
    ],
    "nevermind": [
        "['nev', 'er', 'mahynd']",
        "NFRMNT"
    ],
    "new": [
        "['noo']",
        "N"
    ],
    "newborn": [
        "[noo,bawrn]",
        "NPRN"
    ],
    "newborns": [
        "[noo,bawrn,s]",
        "NPRNS"
    ],
    "newer": [
        "['noo', 'er']",
        "NR"
    ],
    "newest": [
        "[noo,est]",
        "NST"
    ],
    "newly": [
        "['noo', 'lee']",
        "NL"
    ],
    "newport": [
        "[noo,pawrt]",
        "NPRT"
    ],
    "news": [
        "['nooz']",
        "NS"
    ],
    "newspaper": [
        "['nooz', 'pey', 'per']",
        "NSPPR"
    ],
    "newton": [
        "['noot', 'n']",
        "NTN"
    ],
    "next": [
        "['nekst']",
        "NKST"
    ],
    "nexus": [
        "[nek,suhs]",
        "NKSS"
    ],
    "ni": [
        "['nkl']",
        "N"
    ],
    "nice": [
        "['nahys']",
        "NS"
    ],
    "nicely": [
        "['nahys', 'ly']",
        "NSL"
    ],
    "nicer": [
        "['nahys', 'r']",
        "NSR"
    ],
    "nicest": [
        "['nahys', 'st']",
        "NSST"
    ],
    "nicholas": [
        "[nik,uh,luhs]",
        "NXLS"
    ],
    "nick": [
        "['nik']",
        "NK"
    ],
    "nickel": [
        "['nik', 'uhl']",
        "NKL"
    ],
    "nickels": [
        "[nik,uhl,s]",
        "NKLS"
    ],
    "nickname": [
        "['nik', 'neym']",
        "NKNM"
    ],
    "nicknamed": [
        "['nik', 'neym', 'd']",
        "NKNMT"
    ],
    "nicks": [
        "['nik', 's']",
        "NKS"
    ],
    "nicotine": [
        "[nik,uh,teen]",
        "NKTN"
    ],
    "niece": [
        "['nees']",
        "NS"
    ],
    "nieces": [
        "[nees,s]",
        "NSS"
    ],
    "nigerian": [
        "['nahy', 'jeer', 'ee', 'uh', 'n']",
        "NJRN"
    ],
    "night": [
        "['nahyt']",
        "NT"
    ],
    "night's": [
        "['nahyt', \"'s\"]",
        "NTTS"
    ],
    "nightclub": [
        "[nahyt,kluhb]",
        "NTKLP"
    ],
    "nightly": [
        "[nahyt,lee]",
        "NTL"
    ],
    "nightmare": [
        "['nahyt', 'mair']",
        "NTMR"
    ],
    "nightmares": [
        "['nahyt', 'mair', 's']",
        "NTMRS"
    ],
    "nights": [
        "['nahyts']",
        "NTS"
    ],
    "nighttime": [
        "['nahyt', 'tahym']",
        "NTM"
    ],
    "nike": [
        "['nahy', 'kee']",
        "NK"
    ],
    "nike's": [
        "['nahy', 'kee', \"'s\"]",
        "NKS"
    ],
    "nikes": [
        "['nahy', 'kee', 's']",
        "NKS"
    ],
    "nimrod": [
        "[nim,rod]",
        "NMRT"
    ],
    "nine": [
        "['nahyn']",
        "NN"
    ],
    "niner": [
        "['nahy', 'ner']",
        "NNR"
    ],
    "nines": [
        "['nahyn', 's']",
        "NNS"
    ],
    "nineteen": [
        "['nahyn', 'teen']",
        "NNTN"
    ],
    "ninety": [
        "['nahyn', 'tee']",
        "NNT"
    ],
    "ninja": [
        "['nin', 'juh']",
        "NNJ"
    ],
    "ninjas": [
        "[nin,juh,s]",
        "NNJS"
    ],
    "nintendo": [
        "['nin', 'ten', 'doh']",
        "NNTNT"
    ],
    "ninth": [
        "['nahynth']",
        "NN0"
    ],
    "nip": [
        "[nip]",
        "NP"
    ],
    "nipples": [
        "['nip', 'uhl', 's']",
        "NPLS"
    ],
    "nirvana": [
        "[nir,vah,nuh]",
        "NRFN"
    ],
    "nissan": [
        "['nee', 'sahn']",
        "NSN"
    ],
    "nitrous": [
        "['nahy', 'truhs']",
        "NTRS"
    ],
    "nixon": [
        "[nik,suhn]",
        "NKSN"
    ],
    "ni\u00f1o": [
        "['nee', 'nyaw']",
        "NN"
    ],
    "no": [
        "['noh']",
        "N"
    ],
    "no's": [
        "[noh,'s]",
        "NS"
    ],
    "noah": [
        "[noh,uh]",
        "N"
    ],
    "noah's": [
        "['noh', 'uh', \"'s\"]",
        "NS"
    ],
    "nobody": [
        "['noh', 'bod', 'ee']",
        "NPT"
    ],
    "nobody's": [
        "[noh,bod,ee,'s]",
        "NPTS"
    ],
    "nobodys": [
        "[noh,bod,ee,s]",
        "NPTS"
    ],
    "nod": [
        "['nod']",
        "NT"
    ],
    "nodded": [
        "[nod,ded]",
        "NTT"
    ],
    "nodding": [
        "[nod,ding]",
        "NTNK"
    ],
    "noel": [
        "[noh,elfor1]",
        "NL"
    ],
    "nogging": [
        "['nog', 'ing']",
        "NJNK"
    ],
    "noise": [
        "['noiz']",
        "NS"
    ],
    "nominated": [
        "[verbnom,uh,neyt,d]",
        "NMNTT"
    ],
    "non": [
        "['nohnohb', 'stahn', 'te', '']",
        "NN"
    ],
    "nonchalant": [
        "['non', 'shuh', 'lahnt']",
        "NNXLNT"
    ],
    "none": [
        "['nuhn']",
        "NN"
    ],
    "nonsense": [
        "['non', 'sens']",
        "NNSNS"
    ],
    "noodle": [
        "['nood', 'l']",
        "NTL"
    ],
    "noodles": [
        "['nood', 'l', 's']",
        "NTLS"
    ],
    "noon": [
        "['noon']",
        "NN"
    ],
    "noose": [
        "['noos']",
        "NS"
    ],
    "nope": [
        "['nohp']",
        "NP"
    ],
    "nor": [
        "['nawr']",
        "NR"
    ],
    "norm": [
        "[nawrm]",
        "NRM"
    ],
    "normal": [
        "['nawr', 'muhl']",
        "NRML"
    ],
    "normally": [
        "[nawr,muh,lee]",
        "NRML"
    ],
    "norman": [
        "[nawr,muhn]",
        "NRMN"
    ],
    "norris": [
        "['nawr', 'is']",
        "NRS"
    ],
    "north": [
        "['nawrth']",
        "NR0"
    ],
    "northern": [
        "[nawr,thern]",
        "NR0RN"
    ],
    "nose": [
        "['nohz']",
        "NS"
    ],
    "nosebleeds": [
        "['nohz', 'bleed', 's']",
        "NSPLTS"
    ],
    "nosey": [
        "['noh', 'zee']",
        "NS"
    ],
    "nostrils": [
        "['nos', 'truhl', 's']",
        "NSTRLS"
    ],
    "nosy": [
        "[noh,zee]",
        "NS"
    ],
    "not": [
        "['not']",
        "NT"
    ],
    "notch": [
        "['noch']",
        "NX"
    ],
    "note": [
        "['noht']",
        "NT"
    ],
    "notebook": [
        "[noht,book]",
        "NTPK"
    ],
    "notepad": [
        "[noht,pad]",
        "NTPT"
    ],
    "notes": [
        "['noht', 's']",
        "NTS"
    ],
    "nother": [
        "['nuhth', 'er']",
        "N0R"
    ],
    "nothing": [
        "['nuhth', 'ing']",
        "N0NK"
    ],
    "nothing's": [
        "[nuhth,ing,'s]",
        "N0NKKS"
    ],
    "nothings": [
        "[nuhth,ing,s]",
        "N0NKS"
    ],
    "notice": [
        "['noh', 'tis']",
        "NTS"
    ],
    "noticed": [
        "['noh', 'tis', 'd']",
        "NTST"
    ],
    "notices": [
        "['noh', 'tis', 's']",
        "NTSS"
    ],
    "notion": [
        "[noh,shuhn]",
        "NXN"
    ],
    "notorious": [
        "[noh,tawr,ee,uhs]",
        "NTRS"
    ],
    "nouns": [
        "[noun,s]",
        "NNS"
    ],
    "nourishment": [
        "[nur,ish,muhnt]",
        "NRXMNT"
    ],
    "nova": [
        "[noh,vuh]",
        "NF"
    ],
    "november": [
        "[noh,vem,ber]",
        "NFMPR"
    ],
    "now": [
        "['nou']",
        "N"
    ],
    "nowadays": [
        "['nou', 'uh', 'deyz']",
        "NTS"
    ],
    "nowhere": [
        "['noh', 'hwair']",
        "NR"
    ],
    "nu": [
        "['noo']",
        "N"
    ],
    "nubians": [
        "[noo,bee,uhn,s]",
        "NPNS"
    ],
    "nude": [
        "['nood']",
        "NT"
    ],
    "nuff": [
        "[\"'-\", 'nuhf']",
        "NF"
    ],
    "nugget": [
        "[nuhg,it]",
        "NKT"
    ],
    "nuggets": [
        "['nuhg', 'it', 's']",
        "NKTS"
    ],
    "nuisance": [
        "[noo,suhns]",
        "NSNS"
    ],
    "numb": [
        "['nuhm']",
        "NMP"
    ],
    "number": [
        "['nuhm', 'ber']",
        "NMPR"
    ],
    "numbers": [
        "['nuhm', 'berz']",
        "NMPRS"
    ],
    "numerous": [
        "['noo', 'mer', 'uhs']",
        "NMRS"
    ],
    "nun": [
        "['nuhn']",
        "NN"
    ],
    "nuns": [
        "['nuhn', 's']",
        "NNS"
    ],
    "nurse": [
        "['nurs']",
        "NRS"
    ],
    "nursed": [
        "[nurs,d]",
        "NRST"
    ],
    "nursery": [
        "['nur', 'suh', 'ree']",
        "NRSR"
    ],
    "nurses": [
        "[nurs,s]",
        "NRSS"
    ],
    "nut": [
        "['nuht']",
        "NT"
    ],
    "nuts": [
        "['nuhts']",
        "NTS"
    ],
    "nutted": [
        "['nuht', 'ted']",
        "NTT"
    ],
    "nutting": [
        "['nuht', 'ing']",
        "NTNK"
    ],
    "nutty": [
        "[nuht,ee]",
        "NT"
    ],
    "nylon": [
        "[nahy,lon]",
        "NLN"
    ],
    "nympho": [
        "[nim,foh]",
        "NMF"
    ],
    "oak": [
        "[ohk]",
        "AK"
    ],
    "oakland": [
        "['ohk', 'luhnd']",
        "AKLNT"
    ],
    "oakley": [
        "[ohk,lee]",
        "AKL"
    ],
    "oasis": [
        "[oh,ey,sis]",
        "ASS"
    ],
    "oath": [
        "['ohth']",
        "A0"
    ],
    "oats": [
        "[oht,s]",
        "ATS"
    ],
    "ob": [
        "[awb]",
        "AP"
    ],
    "obama": [
        "['oh', 'bah', 'muh']",
        "APM"
    ],
    "obese": [
        "['oh', 'bees']",
        "APS"
    ],
    "obey": [
        "[oh,bey]",
        "AP"
    ],
    "obituary": [
        "[oh,bich,oo,er,ee]",
        "APTR"
    ],
    "object": [
        "[nounob,jikt]",
        "APJKT"
    ],
    "objects": [
        "[nounob,jikt,s]",
        "APJKTS"
    ],
    "obligated": [
        "[verbob,li,geyt,d]",
        "APLKTT"
    ],
    "obliterated": [
        "[uh,blit,uh,reyt,d]",
        "APLTRTT"
    ],
    "obnoxious": [
        "[uhb,nok,shuhs]",
        "APNKSS"
    ],
    "observe": [
        "['uhb', 'zurv']",
        "APSRF"
    ],
    "obsessed": [
        "['uhb', 'sest']",
        "APSST"
    ],
    "obsession": [
        "[uhb,sesh,uhn]",
        "APSSN"
    ],
    "obsolete": [
        "['ob', 'suh', 'leet']",
        "APSLT"
    ],
    "obstacle": [
        "[ob,stuh,kuhl]",
        "APSTKL"
    ],
    "obstacles": [
        "['ob', 'stuh', 'kuhl', 's']",
        "APSTKLS"
    ],
    "obtain": [
        "[uhb,teyn]",
        "APTN"
    ],
    "obvious": [
        "['ob', 'vee', 'uhs']",
        "APFS"
    ],
    "obviously": [
        "[ob,vee,uhs,ly]",
        "APFSL"
    ],
    "oc": [
        [
            "oh",
            "see"
        ],
        "AK"
    ],
    "occasion": [
        "['uh', 'key', 'zhuhn']",
        "AKSN"
    ],
    "occasions": [
        "['uh', 'key', 'zhuhn', 's']",
        "AKSNS"
    ],
    "occupation": [
        "[ok,yuh,pey,shuhn]",
        "AKPXN"
    ],
    "occupy": [
        "[ok,yuh,pahy]",
        "AKP"
    ],
    "occur": [
        "[uh,kur]",
        "AKR"
    ],
    "ocean": [
        "['oh', 'shuhn']",
        "ASN"
    ],
    "octagon": [
        "['ok', 'tuh', 'gon']",
        "AKTKN"
    ],
    "octane": [
        "[ok,teyn]",
        "AKTN"
    ],
    "october": [
        "[ok,toh,ber]",
        "AKTPR"
    ],
    "october's": [
        "[ok,toh,ber,'s]",
        "AKTPRRS"
    ],
    "octopus": [
        "[ok,tuh,puhs]",
        "AKTPS"
    ],
    "od": [
        "['od']",
        "AT"
    ],
    "odd": [
        "[od]",
        "AT"
    ],
    "odds": [
        "[odz]",
        "ATS"
    ],
    "ode": [
        "[ohd]",
        "AT"
    ],
    "odor": [
        "['oh', 'der']",
        "ATR"
    ],
    "odyssey": [
        "[od,uh,see]",
        "ATS"
    ],
    "of": [
        "['uhv']",
        "AF"
    ],
    "off": [
        "['awf']",
        "AF"
    ],
    "offed": [
        "[awf,ed]",
        "AFT"
    ],
    "offend": [
        "[uh,fend]",
        "AFNT"
    ],
    "offended": [
        "['uh', 'fend', 'ed']",
        "AFNTT"
    ],
    "offender": [
        "[uh,fend,er]",
        "AFNTR"
    ],
    "offenders": [
        "['uh', 'fend', 'ers']",
        "AFNTRS"
    ],
    "offending": [
        "['uh', 'fend', 'ing']",
        "AFNTNK"
    ],
    "offense": [
        "['uh', 'fensorfor79']",
        "AFNS"
    ],
    "offensive": [
        "['uh', 'fen', 'sivorfor4']",
        "AFNSF"
    ],
    "offer": [
        "['aw', 'fer']",
        "AFR"
    ],
    "offered": [
        "['aw', 'fer', 'ed']",
        "AFRT"
    ],
    "offering": [
        "[aw,fer,ing]",
        "AFRNK"
    ],
    "offers": [
        "['aw', 'fer', 's']",
        "AFRS"
    ],
    "office": [
        "['aw', 'fis']",
        "AFS"
    ],
    "officer": [
        "['aw', 'fuh', 'ser']",
        "AFSR"
    ],
    "officers": [
        "['aw', 'fuh', 'ser', 's']",
        "AFSRS"
    ],
    "official": [
        "[uh,fish,uhl]",
        "AFSL"
    ],
    "officially": [
        "[uh,fish,uhl,ly]",
        "AFSL"
    ],
    "offs": [
        "[awf,s]",
        "AFS"
    ],
    "offset": [
        "['noun']",
        "AFST"
    ],
    "offspring": [
        "['awf', 'spring']",
        "AFSPRNK"
    ],
    "offsprings": [
        "['awf', 'spring', 's']",
        "AFSPRNKS"
    ],
    "often": [
        "['aw', 'fuhn']",
        "AFTN"
    ],
    "oh": [
        "['oh']",
        "A"
    ],
    "oh's": [
        "[oh,'s]",
        "AS"
    ],
    "ohio": [
        "[oh,hahy,oh]",
        "AH"
    ],
    "oil": [
        "['oil']",
        "AL"
    ],
    "oink": [
        "['oingk']",
        "ANK"
    ],
    "ok": [
        "['oh', 'key']",
        "AK"
    ],
    "okay": [
        "['oh', 'key']",
        "AK"
    ],
    "oklahoma": [
        "[oh,kluh,hoh,muh]",
        "AKLHM"
    ],
    "old": [
        "['ohld']",
        "ALT"
    ],
    "older": [
        "['ohl', 'der']",
        "ALTR"
    ],
    "oldest": [
        "['ohl', 'dist']",
        "ALTST"
    ],
    "olive": [
        "['ol', 'iv']",
        "ALF"
    ],
    "oliver": [
        "[ol,uh,ver]",
        "ALFR"
    ],
    "olympians": [
        "['uh', 'lim', 'pee', 'uhn', 's']",
        "ALMPNS"
    ],
    "olympics": [
        "[uh,lim,pik,s]",
        "ALMPKS"
    ],
    "omega": [
        "['oh', 'mee', 'guh']",
        "AMK"
    ],
    "omelette": [
        "[om,lit,te]",
        "AMLT"
    ],
    "omen": [
        "[oh,muhn]",
        "AMN"
    ],
    "on": [
        "['on']",
        "AN"
    ],
    "once": [
        "['wuhns']",
        "ANS"
    ],
    "one": [
        "['wuhn']",
        "AN"
    ],
    "one's": [
        "['wuhn', \"'s\"]",
        "ANS"
    ],
    "oner": [
        "[wuhn,r]",
        "ANR"
    ],
    "ones": [
        "['wuhn', 's']",
        "ANS"
    ],
    "onion": [
        "['uhn', 'yuhn']",
        "ANN"
    ],
    "onions": [
        "['uhn', 'yuhnz']",
        "ANNS"
    ],
    "online": [
        "['on', 'lahyn']",
        "ANLN"
    ],
    "only": [
        "['ohn', 'lee']",
        "ANL"
    ],
    "onset": [
        "[on,set]",
        "ANST"
    ],
    "onto": [
        "['on', 'too']",
        "ANT"
    ],
    "onyx": [
        "['on', 'iks']",
        "ANKS"
    ],
    "oodles": [
        "[ood,lz]",
        "ATLS"
    ],
    "ooh": [
        "['oo']",
        "A"
    ],
    "oops": [
        "['oops']",
        "APS"
    ],
    "ooze": [
        "['ooz']",
        "AS"
    ],
    "oozy": [
        "[oo,zee]",
        "AS"
    ],
    "open": [
        "['oh', 'puhn']",
        "APN"
    ],
    "opened": [
        "['oh', 'puhn', 'ed']",
        "APNT"
    ],
    "opening": [
        "[oh,puh,ning]",
        "APNNK"
    ],
    "openly": [
        "[oh,puhn,ly]",
        "APNL"
    ],
    "opens": [
        "[oh,puhn,s]",
        "APNS"
    ],
    "opera": [
        "['op', 'er', 'uh']",
        "APR"
    ],
    "operate": [
        "['op', 'uh', 'reyt']",
        "APRT"
    ],
    "operation": [
        "[op,uh,rey,shuhn]",
        "APRXN"
    ],
    "operator": [
        "[op,uh,rey,ter]",
        "APRTR"
    ],
    "opinion": [
        "['uh', 'pin', 'yuhn']",
        "APNN"
    ],
    "opinionated": [
        "[uh,pin,yuh,ney,tid]",
        "APNNTT"
    ],
    "opinions": [
        "['uh', 'pin', 'yuhn', 's']",
        "APNNS"
    ],
    "opponent": [
        "['uh', 'poh', 'nuhnt']",
        "APNNT"
    ],
    "opponents": [
        "['uh', 'poh', 'nuhnt', 's']",
        "APNNTS"
    ],
    "opportunity": [
        "[op,er,too,ni,tee]",
        "APRTNT"
    ],
    "oppose": [
        "[uh,pohz]",
        "APS"
    ],
    "opposite": [
        "['op', 'uh', 'zit']",
        "APST"
    ],
    "opposites": [
        "[op,uh,zit,s]",
        "APSTS"
    ],
    "opposition": [
        "['op', 'uh', 'zish', 'uhn']",
        "APSXN"
    ],
    "ops": [
        "['ops']",
        "APS"
    ],
    "optimistic": [
        "[op,tuh,mis,tik]",
        "APTMSTK"
    ],
    "option": [
        "['op', 'shuhn']",
        "APXN"
    ],
    "options": [
        "['op', 'shuhn', 's']",
        "APXNS"
    ],
    "opus": [
        "[oh,puhs]",
        "APS"
    ],
    "or": [
        "['awr']",
        "AR"
    ],
    "oracle": [
        "[awr,uh,kuhl]",
        "ARKL"
    ],
    "oral": [
        "['awr', 'uhl']",
        "ARL"
    ],
    "orange": [
        "['awr', 'inj']",
        "ARNJ"
    ],
    "orbit": [
        "['awr', 'bit']",
        "ARPT"
    ],
    "orbits": [
        "[awr,bit,s]",
        "ARPTS"
    ],
    "order": [
        "['awr', 'der']",
        "ARTR"
    ],
    "ordered": [
        "['awr', 'derd']",
        "ARTRT"
    ],
    "ordering": [
        "['awr', 'der', 'ing']",
        "ARTRNK"
    ],
    "orders": [
        "['awr', 'der', 's']",
        "ARTRS"
    ],
    "ordinary": [
        "['awr', 'dn', 'er', 'ee']",
        "ARTNR"
    ],
    "ore": [
        "['awr']",
        "AR"
    ],
    "organized": [
        "[awr,guh,nahyzd]",
        "ARKNST"
    ],
    "organs": [
        "['awr', 'guhn', 's']",
        "ARKNS"
    ],
    "orgasm": [
        "[awr,gaz,uhm]",
        "ARKSM"
    ],
    "orgy": [
        "[awr,jee]",
        "ARJ"
    ],
    "orientated": [
        "[awr,ee,uhn,teyt,d]",
        "ARNTTT"
    ],
    "original": [
        "['uh', 'rij', 'uh', 'nl']",
        "ARJNL"
    ],
    "orlando": [
        "['awr', 'lan', 'doh']",
        "ARLNT"
    ],
    "orleans": [
        [
            "awr",
            "lee",
            "ahnz"
        ],
        "ARLNS"
    ],
    "ornament": [
        "['nounawr', 'nuh', 'muhnt']",
        "ARNMNT"
    ],
    "orphan": [
        "[awr,fuhn]",
        "ARFN"
    ],
    "orphans": [
        "['awr', 'fuhn', 's']",
        "ARFNS"
    ],
    "os": [
        "['os']",
        "AS"
    ],
    "osama": [
        [
            "os",
            "ah",
            "mah"
        ],
        "ASM"
    ],
    "oscar": [
        "['os', 'ker']",
        "ASKR"
    ],
    "ostrich": [
        "[aw,strich]",
        "ASTRX"
    ],
    "other": [
        "['uhth', 'er']",
        "A0R"
    ],
    "others": [
        "['uhth', 'er', 's']",
        "A0RS"
    ],
    "otherwise": [
        "[uhth,er,wahyz]",
        "A0RS"
    ],
    "ought": [
        "['awt']",
        "AT"
    ],
    "oui": [
        "['wee']",
        "A"
    ],
    "ounce": [
        "['ouns']",
        "ANS"
    ],
    "ounces": [
        "['ouns', 's']",
        "ANSS"
    ],
    "our": [
        "['ouuhr']",
        "AR"
    ],
    "ours": [
        "['ouuhrz']",
        "ARS"
    ],
    "out": [
        "['out']",
        "AT"
    ],
    "outbreak": [
        "[out,breyk]",
        "ATPRK"
    ],
    "outcast": [
        "[out,kast]",
        "ATKST"
    ],
    "outcome": [
        "['out', 'kuhm']",
        "ATKM"
    ],
    "outdated": [
        "[out,dey,tid]",
        "ATTT"
    ],
    "outdoors": [
        "[out,dawrz]",
        "ATRS"
    ],
    "outer": [
        "['ou', 'ter']",
        "ATR"
    ],
    "outfielder": [
        "['out', 'feel', 'der']",
        "ATFLTR"
    ],
    "outfit": [
        "['out', 'fit']",
        "ATFT"
    ],
    "outfit's": [
        "[out,fit,'s]",
        "ATFTTS"
    ],
    "outfits": [
        "['out', 'fit', 's']",
        "ATFTS"
    ],
    "outlandish": [
        "['out', 'lan', 'dish']",
        "ATLNTX"
    ],
    "outlast": [
        "[out,last]",
        "ATLST"
    ],
    "outlaw": [
        "[out,law]",
        "ATL"
    ],
    "outlet": [
        "[out,let]",
        "ATLT"
    ],
    "outline": [
        "['out', 'lahyn']",
        "ATLN"
    ],
    "outrageous": [
        "[out,rey,juhs]",
        "ATRJS"
    ],
    "outs": [
        "['out', 's']",
        "ATS"
    ],
    "outshine": [
        "[out,shahyn]",
        "ATXN"
    ],
    "outside": [
        "['nounout', 'sahyd']",
        "ATST"
    ],
    "outsiders": [
        "[out,sahy,der,s]",
        "ATSTRS"
    ],
    "outstanding": [
        "['out', 'stan', 'ding']",
        "ATSTNTNK"
    ],
    "ova": [
        "['oh', 'vuh']",
        "AF"
    ],
    "oval": [
        "[oh,vuhl]",
        "AFL"
    ],
    "ovation": [
        "[oh,vey,shuhn]",
        "AFXN"
    ],
    "oven": [
        "['uhv', 'uhn']",
        "AFN"
    ],
    "over": [
        "['oh', 'ver']",
        "AFR"
    ],
    "overachiever": [
        "['oh', 'ver', 'uh', 'cheev', 'r']",
        "AFRXFR"
    ],
    "overall": [
        "[adverboh,ver,awl]",
        "AFRL"
    ],
    "overboard": [
        "[oh,ver,bawrd]",
        "AFRPRT"
    ],
    "overcome": [
        "['oh', 'ver', 'kuhm']",
        "AFRKM"
    ],
    "overcrowded": [
        "['oh', 'ver', 'kroud', 'ed']",
        "AFRKRTT"
    ],
    "overdoing": [
        "['oh', 'ver', 'doo', 'ing']",
        "AFRTNK"
    ],
    "overdose": [
        "['nounoh', 'ver', 'dohs']",
        "AFRTS"
    ],
    "overdosed": [
        "['nounoh', 'ver', 'dohs', 'd']",
        "AFRTST"
    ],
    "overdrive": [
        "['verboh', 'ver', 'drahyv']",
        "AFRTRF"
    ],
    "overdue": [
        "['oh', 'ver', 'doo']",
        "AFRT"
    ],
    "overflow": [
        "[verboh,ver,floh]",
        "AFRFL"
    ],
    "overflowing": [
        "[verboh,ver,floh,ing]",
        "AFRFLNK"
    ],
    "overgrown": [
        "[oh,ver,groh,n]",
        "AFRKRN"
    ],
    "overheard": [
        "['oh', 'ver', 'heer', 'd']",
        "AFRRT"
    ],
    "overload": [
        "['verboh', 'ver', 'lohd']",
        "AFRLT"
    ],
    "overlook": [
        "['verboh', 'ver', 'look']",
        "AFRLK"
    ],
    "overly": [
        "[oh,ver,lee]",
        "AFRL"
    ],
    "overnight": [
        "['adverboh', 'ver', 'nahyt']",
        "AFRNT"
    ],
    "overrated": [
        "[oh,ver,reyt,d]",
        "AFRTT"
    ],
    "overseas": [
        "['adverb']",
        "AFRSS"
    ],
    "oversee": [
        "[oh,ver,see]",
        "AFRS"
    ],
    "overtime": [
        "[noun]",
        "AFRTM"
    ],
    "overzealous": [
        "['oh', 'ver', 'zel', 'uhs']",
        "AFRSLS"
    ],
    "ow": [
        "['ou']",
        "A"
    ],
    "owe": [
        "['oh']",
        "A"
    ],
    "owed": [
        "[oh,d]",
        "AT"
    ],
    "owens": [
        "['oh', 'uhnz']",
        "ANS"
    ],
    "owl": [
        "['oul']",
        "AL"
    ],
    "owls": [
        "[oul,s]",
        "ALS"
    ],
    "own": [
        "['ohn']",
        "AN"
    ],
    "owned": [
        "[ohn,ed]",
        "ANT"
    ],
    "owner": [
        "['oh', 'ner']",
        "ANR"
    ],
    "owners": [
        "[oh,ner,s]",
        "ANRS"
    ],
    "owning": [
        "['ohn', 'ing']",
        "ANNK"
    ],
    "owns": [
        "[ohn,s]",
        "ANS"
    ],
    "ox": [
        "['oks']",
        "AKS"
    ],
    "oxycontin": [
        [
            "ok",
            "si",
            "toh",
            "suhn"
        ],
        "AKSKNTN"
    ],
    "oxygen": [
        "['ok', 'si', 'juhn']",
        "AKSJN"
    ],
    "ozone": [
        "['oh', 'zohn']",
        "ASN"
    ],
    "p": [
        "['pee', '']",
        "P"
    ],
    "p's": [
        [
            "pee",
            "es"
        ],
        "PPS"
    ],
    "pa": [
        "['pah']",
        "P"
    ],
    "pablo": [
        "['pah', 'bloh']",
        "PPL"
    ],
    "pac": [
        "['pak']",
        "PK"
    ],
    "pac's": [
        "[pak,'s]",
        "PKKS"
    ],
    "pace": [
        "['peys']",
        "PS"
    ],
    "pacer": [
        "[pey,ser]",
        "PSR"
    ],
    "paces": [
        "[peys,s]",
        "PSS"
    ],
    "pacific": [
        "['puh', 'sif', 'ik']",
        "PSFK"
    ],
    "pacifier": [
        "[pas,uh,fahy,er]",
        "PSF"
    ],
    "pacino": [
        [
            "pa",
            "chee",
            "noh"
        ],
        "PSN"
    ],
    "pack": [
        "['pak']",
        "PK"
    ],
    "package": [
        "['pak', 'ij']",
        "PKJ"
    ],
    "packages": [
        "['pak', 'ij', 's']",
        "PKJS"
    ],
    "packaging": [
        "[pak,uh,jing]",
        "PKJNK"
    ],
    "packed": [
        "['pakt']",
        "PKT"
    ],
    "packer": [
        "[pak,er]",
        "PKR"
    ],
    "packers": [
        "[pak,er,s]",
        "PKRS"
    ],
    "packing": [
        "['pak', 'ing']",
        "PKNK"
    ],
    "packs": [
        "['pak', 's']",
        "PKS"
    ],
    "pacquiao": [
        [
            "pak",
            "ee",
            "aho"
        ],
        "PK"
    ],
    "pact": [
        "[pakt]",
        "PKT"
    ],
    "pad": [
        "['pad']",
        "PT"
    ],
    "padded": [
        "[pad,ded]",
        "PTT"
    ],
    "paddle": [
        "['pad', 'l']",
        "PTL"
    ],
    "paddy": [
        "['pad', 'ee']",
        "PT"
    ],
    "pads": [
        "['pad', 's']",
        "PTS"
    ],
    "page": [
        "['peyj']",
        "PJ"
    ],
    "pager": [
        "[pey,jer]",
        "PKR"
    ],
    "pagers": [
        "[pey,jer,s]",
        "PKRS"
    ],
    "pages": [
        "['peyj', 's']",
        "PJS"
    ],
    "paging": [
        "[pey,jing]",
        "PJNK"
    ],
    "paid": [
        "['peyd']",
        "PT"
    ],
    "pain": [
        "['peyn']",
        "PN"
    ],
    "painkiller": [
        "[peyn,kil,er]",
        "PNKLR"
    ],
    "painkillers": [
        "['peyn', 'kil', 'er', 's']",
        "PNKLRS"
    ],
    "pains": [
        "['peyn', 's']",
        "PNS"
    ],
    "paint": [
        "['peynt']",
        "PNT"
    ],
    "painted": [
        "['peyn', 'tid']",
        "PNTT"
    ],
    "painter": [
        "[peyn,ter]",
        "PNTR"
    ],
    "painters": [
        "[peyn,ter,s]",
        "PNTRS"
    ],
    "painting": [
        "['peyn', 'ting']",
        "PNTNK"
    ],
    "pair": [
        "['pair']",
        "PR"
    ],
    "pairs": [
        "[pair,s]",
        "PRS"
    ],
    "pajamas": [
        "['puh', 'jah', 'muhz']",
        "PJMS"
    ],
    "pakistan": [
        "['pak', 'uh', 'stan']",
        "PKSTN"
    ],
    "pal": [
        "[pal]",
        "PL"
    ],
    "palace": [
        "['pal', 'is']",
        "PLS"
    ],
    "pale": [
        "['peyl']",
        "PL"
    ],
    "pall": [
        "[pawl]",
        "PL"
    ],
    "pallbearer": [
        "[pawl,bair,er]",
        "PLPRR"
    ],
    "palm": [
        "['pahm']",
        "PLM"
    ],
    "palmer": [
        "[pah,mer]",
        "PLMR"
    ],
    "palms": [
        "['pahm', 's']",
        "PLMS"
    ],
    "pamper": [
        "['pam', 'per']",
        "PMPR"
    ],
    "pampered": [
        "[pam,per,ed]",
        "PMPRT"
    ],
    "pampers": [
        "['pam', 'per', 's']",
        "PMPRS"
    ],
    "pan": [
        "['pan']",
        "PN"
    ],
    "pancake": [
        "['pan', 'keyk']",
        "PNKK"
    ],
    "pancakes": [
        "['pan', 'keyk', 's']",
        "PNKKS"
    ],
    "pander": [
        "['pan', 'der']",
        "PNTR"
    ],
    "pandora": [
        "['pan', 'dawr', 'uh']",
        "PNTR"
    ],
    "pane": [
        "[peyn]",
        "PN"
    ],
    "panel": [
        "[pan,l]",
        "PNL"
    ],
    "panic": [
        "['pan', 'ik']",
        "PNK"
    ],
    "panorama": [
        "['pan', 'uh', 'ram', 'uh']",
        "PNRM"
    ],
    "pans": [
        "['pan', 's']",
        "PNS"
    ],
    "pant": [
        "[pant]",
        "PNT"
    ],
    "panther": [
        "['pan', 'ther']",
        "PN0R"
    ],
    "panthers": [
        "[pan,ther,s]",
        "PN0RS"
    ],
    "panties": [
        "['pan', 'teez']",
        "PNTS"
    ],
    "pantry": [
        "['pan', 'tree']",
        "PNTR"
    ],
    "pants": [
        "['pants']",
        "PNTS"
    ],
    "panty": [
        "['pan', 'tee']",
        "PNT"
    ],
    "pap": [
        "[pap]",
        "PP"
    ],
    "papa": [
        "['pah', 'puh']",
        "PP"
    ],
    "papa's": [
        "['pah', 'puh', \"'s\"]",
        "PPS"
    ],
    "paper": [
        "['pey', 'per']",
        "PPR"
    ],
    "papers": [
        "['pey', 'per', 's']",
        "PPRS"
    ],
    "paperwork": [
        "[pey,per,wurk]",
        "PPRRK"
    ],
    "papi": [
        [
            "pap",
            "ahy"
        ],
        "PP"
    ],
    "papoose": [
        "['pa', 'poos']",
        "PPS"
    ],
    "par": [
        "['pahr']",
        "PR"
    ],
    "para": [
        "[pah,rah]",
        "PR"
    ],
    "parachute": [
        "['par', 'uh', 'shoot']",
        "PRKT"
    ],
    "parade": [
        "['puh', 'reyd']",
        "PRT"
    ],
    "paradise": [
        "['par', 'uh', 'dahys']",
        "PRTS"
    ],
    "parakeet": [
        "[par,uh,keet]",
        "PRKT"
    ],
    "parallel": [
        "['par', 'uh', 'lel']",
        "PRLL"
    ],
    "paralyze": [
        "['par', 'uh', 'lahyz']",
        "PRLS"
    ],
    "paralyzed": [
        "[par,uh,lahyz,d]",
        "PRLST"
    ],
    "paramedics": [
        "['par', 'uh', 'med', 'ik', 's']",
        "PRMTKS"
    ],
    "paranoia": [
        "['par', 'uh', 'noi', 'uh']",
        "PRN"
    ],
    "paranoid": [
        "['par', 'uh', 'noid']",
        "PRNT"
    ],
    "paraphernalia": [
        "['par', 'uh', 'fer', 'neyl', 'yuh']",
        "PRFRNL"
    ],
    "pardon": [
        "['pahr', 'dn']",
        "PRTN"
    ],
    "parent": [
        "[pair,uhnt]",
        "PRNT"
    ],
    "parents": [
        "['pair', 'uhnt', 's']",
        "PRNTS"
    ],
    "paris": [
        "['par', 'is']",
        "PRS"
    ],
    "park": [
        "['pahrk']",
        "PRK"
    ],
    "parka": [
        "['pahr', 'kuh']",
        "PRK"
    ],
    "parked": [
        "['pahrk', 'ed']",
        "PRKT"
    ],
    "parker": [
        "['pahr', 'ker']",
        "PRKR"
    ],
    "parking": [
        "['par', 'king']",
        "PRKNK"
    ],
    "parks": [
        "['pahrks']",
        "PRKS"
    ],
    "parlay": [
        "['pahr', 'ley']",
        "PRL"
    ],
    "parliament": [
        "['pahr', 'luh', 'muhntor']",
        "PRLMNT"
    ],
    "parlor": [
        "['pahr', 'ler']",
        "PRLR"
    ],
    "parlors": [
        "['pahr', 'ler', 's']",
        "PRLRS"
    ],
    "parole": [
        "['puh', 'rohl']",
        "PRL"
    ],
    "parrot": [
        "[par,uht]",
        "PRT"
    ],
    "part": [
        "['pahrt']",
        "PRT"
    ],
    "parted": [
        "[par,tid]",
        "PRTT"
    ],
    "participation": [
        "['pahr', 'tis', 'uh', 'pey', 'shuhn']",
        "PRTSPXN"
    ],
    "particular": [
        "[per,tik,yuh,ler]",
        "PRTKLR"
    ],
    "partition": [
        "[pahr,tish,uhn]",
        "PRTXN"
    ],
    "partly": [
        "['pahrt', 'lee']",
        "PRTL"
    ],
    "partner": [
        "['pahrt', 'ner']",
        "PRTNR"
    ],
    "partner's": [
        "['pahrt', 'ner', \"'s\"]",
        "PRTNRRS"
    ],
    "partners": [
        "['pahrt', 'ner', 's']",
        "PRTNRS"
    ],
    "parts": [
        "['pahrt', 's']",
        "PRTS"
    ],
    "party": [
        "['pahr', 'tee']",
        "PRT"
    ],
    "party's": [
        "[pahr,tee,'s]",
        "PRTS"
    ],
    "partying": [
        "['pahr', 'tee', 'ing']",
        "PRTNK"
    ],
    "pas": [
        "[pah]",
        "PS"
    ],
    "pass": [
        "['pas']",
        "PS"
    ],
    "passed": [
        "['past']",
        "PST"
    ],
    "passenger": [
        "['pas', 'uhn', 'jer']",
        "PSNKR"
    ],
    "passengers": [
        "['pas', 'uhn', 'jer', 's']",
        "PSNKRS"
    ],
    "passes": [
        "['pas', 'es']",
        "PSS"
    ],
    "passing": [
        "['pas', 'ing']",
        "PSNK"
    ],
    "passion": [
        "['pash', 'uhn']",
        "PSN"
    ],
    "passionate": [
        "[pash,uh,nit]",
        "PSNT"
    ],
    "passive": [
        "[pas,iv]",
        "PSF"
    ],
    "passport": [
        "[pas,pawrt]",
        "PSPRT"
    ],
    "passports": [
        "[pas,pawrt,s]",
        "PSPRTS"
    ],
    "password": [
        "['pas', 'wurd']",
        "PSRT"
    ],
    "past": [
        "['past']",
        "PST"
    ],
    "pasta": [
        "['pah', 'stuh']",
        "PST"
    ],
    "pastel": [
        "[pa,stel]",
        "PSTL"
    ],
    "pastor": [
        "['pas', 'ter']",
        "PSTR"
    ],
    "pastors": [
        "['pas', 'ter', 's']",
        "PSTRS"
    ],
    "pastry": [
        "[pey,stree]",
        "PSTR"
    ],
    "pat": [
        "['pat']",
        "PT"
    ],
    "patch": [
        "['pach']",
        "PX"
    ],
    "patches": [
        "['pach', 'es']",
        "PXS"
    ],
    "patek": [
        [
            "pah",
            "teyk"
        ],
        "PTK"
    ],
    "patent": [
        "[pat,ntorfor10]",
        "PTNT"
    ],
    "path": [
        "['path']",
        "P0"
    ],
    "pathetic": [
        "[puh,thet,ik]",
        "P0TK"
    ],
    "pathfinder": [
        "[path,fahyn,der]",
        "P0FNTR"
    ],
    "patience": [
        "['pey', 'shuhns']",
        "PTNS"
    ],
    "patient": [
        "['pey', 'shuhnt']",
        "PTNT"
    ],
    "patiently": [
        "['pey', 'shuhnt', 'ly']",
        "PTNTL"
    ],
    "patients": [
        "[pey,shuhnt,s]",
        "PTNTS"
    ],
    "patio": [
        "[pat,ee,oh]",
        "PT"
    ],
    "patricia": [
        "['puh', 'trish', 'uh']",
        "PTRS"
    ],
    "patrick": [
        "['pa', 'trik']",
        "PTRK"
    ],
    "patrol": [
        "[puh,trohl]",
        "PTRL"
    ],
    "patr\u00f3n": [
        "['pah', 'trawn']",
        "PTRN"
    ],
    "pattern": [
        "['pat', 'ern']",
        "PTRN"
    ],
    "patty": [
        "['pat', 'ee']",
        "PT"
    ],
    "paul": [
        "['pawlfor13']",
        "PL"
    ],
    "pause": [
        "['pawz']",
        "PS"
    ],
    "paused": [
        "[pawz,d]",
        "PST"
    ],
    "paved": [
        "[peyv,d]",
        "PFT"
    ],
    "pavement": [
        "['peyv', 'muhnt']",
        "PFMNT"
    ],
    "paving": [
        "[pey,ving]",
        "PFNK"
    ],
    "paw": [
        "['paw']",
        "P"
    ],
    "pawn": [
        "[pawn]",
        "PN"
    ],
    "pay": [
        "['pey']",
        "P"
    ],
    "payback": [
        "['pey', 'bak']",
        "PPK"
    ],
    "paycheck": [
        "[pey,chek]",
        "PXK"
    ],
    "paychecks": [
        "['pey', 'chek', 's']",
        "PXKS"
    ],
    "payday": [
        "[pey,dey]",
        "PT"
    ],
    "payed": [
        "['pey', 'ed']",
        "PT"
    ],
    "paying": [
        "['pey', 'ing']",
        "PNK"
    ],
    "payment": [
        "['pey', 'muhnt']",
        "PMNT"
    ],
    "payments": [
        "['pey', 'muhnt', 's']",
        "PMNTS"
    ],
    "payola": [
        "['pey', 'oh', 'luh']",
        "PL"
    ],
    "payroll": [
        "['pey', 'rohl']",
        "PRL"
    ],
    "payrolls": [
        "[pey,rohl,s]",
        "PRLS"
    ],
    "pays": [
        "[pey,s]",
        "PS"
    ],
    "pe": [
        "['pey']",
        "P"
    ],
    "pea": [
        "[pee]",
        "P"
    ],
    "peace": [
        "['pees']",
        "PS"
    ],
    "peaceful": [
        "[pees,fuhl]",
        "PSFL"
    ],
    "peach": [
        "['peech']",
        "PX"
    ],
    "peaches": [
        "['peech', 'es']",
        "PXS"
    ],
    "peacoat": [
        "[pee,koht]",
        "PKT"
    ],
    "peacock": [
        "['pee', 'kok']",
        "PKK"
    ],
    "peak": [
        "['peek']",
        "PK"
    ],
    "peaking": [
        "['peek', 'ing']",
        "PKNK"
    ],
    "peanut": [
        "['pee', 'nuht']",
        "PNT"
    ],
    "peanuts": [
        "['pee', 'nuht', 's']",
        "PNTS"
    ],
    "pear": [
        "[pair]",
        "PR"
    ],
    "pearl": [
        "['purl']",
        "PRL"
    ],
    "pearls": [
        "['purl', 's']",
        "PRLS"
    ],
    "pearly": [
        "[pur,lee]",
        "PRL"
    ],
    "peas": [
        "[pee,s]",
        "PS"
    ],
    "peasant": [
        "['pez', 'uhnt']",
        "PSNT"
    ],
    "peasants": [
        "['pez', 'uhnt', 's']",
        "PSNTS"
    ],
    "pebble": [
        "[peb,uhl]",
        "PPL"
    ],
    "pebbles": [
        "['peb', 'uhl', 's']",
        "PPLS"
    ],
    "pecan": [
        "['pi', 'kahn']",
        "PKN"
    ],
    "pecking": [
        "['pek', 'ing']",
        "PKNK"
    ],
    "pedal": [
        "['ped', 'lorfor68']",
        "PTL"
    ],
    "pedals": [
        "[ped,lorfor68,s]",
        "PTLS"
    ],
    "peddling": [
        "[ped,ling]",
        "PTLNK"
    ],
    "pedestal": [
        "['ped', 'uh', 'stl']",
        "PTSTL"
    ],
    "pedestrian": [
        "[puh,des,tree,uhn]",
        "PTSTRN"
    ],
    "pedestrians": [
        "[puh,des,tree,uhn,s]",
        "PTSTRNS"
    ],
    "pedicure": [
        "['ped', 'i', 'kyoor']",
        "PTKR"
    ],
    "pedigree": [
        "['ped', 'i', 'gree']",
        "PTKR"
    ],
    "pee": [
        "['pee']",
        "P"
    ],
    "peeing": [
        "[pee,ing]",
        "PNK"
    ],
    "peek": [
        "['peek']",
        "PK"
    ],
    "peeking": [
        "[peek,ing]",
        "PKNK"
    ],
    "peel": [
        "['peel']",
        "PL"
    ],
    "peeled": [
        "['peel', 'ed']",
        "PLT"
    ],
    "peelers": [
        "[pee,ler,s]",
        "PLRS"
    ],
    "peeling": [
        "['pee', 'ling']",
        "PLNK"
    ],
    "peep": [
        "['peep']",
        "PP"
    ],
    "peeped": [
        "['peep', 'ed']",
        "PPT"
    ],
    "peephole": [
        "['peep', 'hohl']",
        "PFL"
    ],
    "peeping": [
        "['peep', 'ing']",
        "PPNK"
    ],
    "peeps": [
        "[peeps]",
        "PPS"
    ],
    "peers": [
        "['peer', 's']",
        "PRS"
    ],
    "peewee": [
        "['pee', 'wee']",
        "P"
    ],
    "pelican": [
        "['pel', 'i', 'kuhn']",
        "PLKN"
    ],
    "pen": [
        "['pen']",
        "PN"
    ],
    "penalty": [
        "['pen', 'l', 'tee']",
        "PNLT"
    ],
    "pencil": [
        "['pen', 'suhl']",
        "PNSL"
    ],
    "pencils": [
        "[pen,suhl,s]",
        "PNSLS"
    ],
    "pendant": [
        "['pen', 'duhnt']",
        "PNTNT"
    ],
    "pendent": [
        "['pen', 'duhnt']",
        "PNTNT"
    ],
    "penetrate": [
        "['pen', 'i', 'treyt']",
        "PNTRT"
    ],
    "penetrating": [
        "[pen,i,trey,ting]",
        "PNTRTNK"
    ],
    "penetration": [
        "[pen,i,trey,shuhn]",
        "PNTRXN"
    ],
    "penguin": [
        "['peng', 'gwin']",
        "PNKN"
    ],
    "penis": [
        "[pee,nis]",
        "PNS"
    ],
    "penitentiary": [
        "['pen', 'i', 'ten', 'shuh', 'ree']",
        "PNTNXR"
    ],
    "penn": [
        "['pen']",
        "PN"
    ],
    "penned": [
        "[pen,ned]",
        "PNT"
    ],
    "pennies": [
        "['pen', 'ee', 's']",
        "PNS"
    ],
    "penny": [
        "['pen', 'ee']",
        "PN"
    ],
    "pens": [
        "[pen,s]",
        "PNS"
    ],
    "pension": [
        "['pen', 'shuhn']",
        "PNSN"
    ],
    "pent": [
        "['pent']",
        "PNT"
    ],
    "penthouse": [
        "['pent', 'hous']",
        "PN0S"
    ],
    "peons": [
        "['pee', 'uhn', 's']",
        "PNS"
    ],
    "people": [
        "['pee', 'puhl']",
        "PPL"
    ],
    "people's": [
        "['pee', 'puhl', \"'s\"]",
        "PPLS"
    ],
    "peoples": [
        "['pee', 'puhl', 's']",
        "PPLS"
    ],
    "pep": [
        "[pep]",
        "PP"
    ],
    "pepper": [
        "['pep', 'er']",
        "PPR"
    ],
    "peppermint": [
        "['pep', 'er', 'mint']",
        "PPRMNT"
    ],
    "peppers": [
        "[pep,er,s]",
        "PPRS"
    ],
    "pepsi": [
        [
            "pep",
            "see"
        ],
        "PPS"
    ],
    "perc": [
        "['purk']",
        "PRK"
    ],
    "percent": [
        "['per', 'sent']",
        "PRSNT"
    ],
    "percentage": [
        "[per,sen,tij]",
        "PRSNTJ"
    ],
    "perception": [
        "[per,sep,shuhn]",
        "PRSPXN"
    ],
    "percocet": [
        "['pur', 'kuh', 'set']",
        "PRKST"
    ],
    "percocets": [
        "['pur', 'kuh', 'set', 's']",
        "PRKSTS"
    ],
    "percs": [
        "['purk', 's']",
        "PRKS"
    ],
    "perfect": [
        "['adjective']",
        "PRFKT"
    ],
    "perfected": [
        "[adjective,ed]",
        "PRFKTT"
    ],
    "perfecting": [
        "['adjective', 'ing']",
        "PRFKTNK"
    ],
    "perfection": [
        "[per,fek,shuhn]",
        "PRFKXN"
    ],
    "perfectly": [
        "[pur,fikt,lee]",
        "PRFKTL"
    ],
    "perform": [
        "['per', 'fawrm']",
        "PRFRM"
    ],
    "performance": [
        "[per,fawr,muhns]",
        "PRFRMNS"
    ],
    "performed": [
        "[per,fawrm,ed]",
        "PRFRMT"
    ],
    "performing": [
        "['per', 'fawrm', 'ing']",
        "PRFRMNK"
    ],
    "perfume": [
        "['nounpur', 'fyoom']",
        "PRFM"
    ],
    "perhaps": [
        "[per,haps]",
        "PRPS"
    ],
    "perimeter": [
        "['puh', 'rim', 'i', 'ter']",
        "PRMTR"
    ],
    "period": [
        "['peer', 'ee', 'uhd']",
        "PRT"
    ],
    "peripheral": [
        "['puh', 'rif', 'er', 'uhl']",
        "PRFRL"
    ],
    "perish": [
        "[per,ish]",
        "PRX"
    ],
    "perishing": [
        "[per,i,shing]",
        "PRXNK"
    ],
    "perk": [
        "['purk']",
        "PRK"
    ],
    "perks": [
        "[purk,s]",
        "PRKS"
    ],
    "perky": [
        "['pur', 'kee']",
        "PRK"
    ],
    "perkys": [
        [
            "purk",
            "ees"
        ],
        "PRKS"
    ],
    "perm": [
        "[purm]",
        "PRM"
    ],
    "permanent": [
        "['pur', 'muh', 'nuhnt']",
        "PRMNNT"
    ],
    "permanently": [
        "['pur', 'muh', 'nuhnt', 'ly']",
        "PRMNNTL"
    ],
    "permission": [
        "[per,mish,uhn]",
        "PRMSN"
    ],
    "perms": [
        "[purm,s]",
        "PRMS"
    ],
    "perpetrators": [
        "[pur,pi,trey,ter,s]",
        "PRPTRTRS"
    ],
    "perry": [
        "['per', 'ee']",
        "PR"
    ],
    "persian": [
        "['pur', 'zhuhn']",
        "PRSN"
    ],
    "persistence": [
        "['per', 'sis', 'tuhns']",
        "PRSSTNS"
    ],
    "persistent": [
        "['per', 'sis', 'tuhnt']",
        "PRSSTNT"
    ],
    "person": [
        "['pur', 'suhn']",
        "PRSN"
    ],
    "persona": [
        "['per', 'soh', 'nuh']",
        "PRSN"
    ],
    "personal": [
        "['pur', 'suh', 'nl']",
        "PRSNL"
    ],
    "personality": [
        "[pur,suh,nal,i,tee]",
        "PRSNLT"
    ],
    "personally": [
        "['pur', 'suh', 'nl', 'ee']",
        "PRSNL"
    ],
    "persons": [
        "[pur,suhn,s]",
        "PRSNS"
    ],
    "perspective": [
        "[per,spek,tiv]",
        "PRSPKTF"
    ],
    "peru": [
        "['puh', 'roo']",
        "PR"
    ],
    "pervert": [
        "[verbper,vurt]",
        "PRFRT"
    ],
    "peso": [
        "['pey', 'soh']",
        "PS"
    ],
    "pesos": [
        "['pey', 'soh', 's']",
        "PSS"
    ],
    "pessimistic": [
        "[pes,uh,mis,tik]",
        "PSMSTK"
    ],
    "pest": [
        "['pest']",
        "PST"
    ],
    "pet": [
        "['pet']",
        "PT"
    ],
    "petal": [
        "[pet,l]",
        "PTL"
    ],
    "petals": [
        "['pet', 'l', 's']",
        "PTLS"
    ],
    "peter": [
        "['pee', 'ter']",
        "PTR"
    ],
    "petite": [
        "['puh', 'teet']",
        "PTT"
    ],
    "petrified": [
        [
            "pe",
            "truh",
            "fahyd"
        ],
        "PTRFT"
    ],
    "petrol": [
        "[pe,truhl]",
        "PTRL"
    ],
    "petty": [
        "['pet', 'ee']",
        "PT"
    ],
    "pew": [
        "['pyoo']",
        "P"
    ],
    "peyton": [
        "['peyt', 'n']",
        "PTN"
    ],
    "ph": [
        "[(pch)]",
        "F"
    ],
    "phantom": [
        "['fan', 'tuhm']",
        "FNTM"
    ],
    "phantoms": [
        "['fan', 'tuhm', 's']",
        "FNTMS"
    ],
    "pharaoh": [
        "['fair', 'oh']",
        "FR"
    ],
    "pharaohs": [
        "[fair,oh,s]",
        "FRS"
    ],
    "pharmacy": [
        "[fahr,muh,see]",
        "FRMS"
    ],
    "phase": [
        "['feyz']",
        "FS"
    ],
    "phases": [
        "[feyz,s]",
        "FSS"
    ],
    "phenomenal": [
        "['fi', 'nom', 'uh', 'nl']",
        "FNMNL"
    ],
    "phenomenon": [
        "['fi', 'nom', 'uh', 'non']",
        "FNMNN"
    ],
    "phifer": [
        [
            "fahy",
            "fur"
        ],
        "FFR"
    ],
    "philanthropist": [
        "[fi,lan,thruh,pist]",
        "FLN0RPST"
    ],
    "philippe": [
        [
            "fil",
            "ip",
            "pey"
        ],
        "FLP"
    ],
    "philly": [
        "['fil', 'ee']",
        "FL"
    ],
    "philosophy": [
        "[fi,los,uh,fee]",
        "FLSF"
    ],
    "phlegm": [
        "['flem']",
        "FLKM"
    ],
    "phoenix": [
        "['fee', 'niks']",
        "FNKS"
    ],
    "phone": [
        "['fohn']",
        "FN"
    ],
    "phones": [
        "['fohn', 's']",
        "FNS"
    ],
    "phoney": [
        "[foh,nee]",
        "FN"
    ],
    "phonics": [
        "[fon,iksorfor2]",
        "FNKS"
    ],
    "phony": [
        "['foh', 'nee']",
        "FN"
    ],
    "photo": [
        "['foh', 'toh']",
        "FT"
    ],
    "photos": [
        "['foh', 'toh', 's']",
        "FTS"
    ],
    "phrase": [
        "['freyz']",
        "FRS"
    ],
    "phrases": [
        "[freyz,s]",
        "FRSS"
    ],
    "physical": [
        "['fiz', 'i', 'kuhl']",
        "FSKL"
    ],
    "physically": [
        "['fiz', 'ik', 'lee']",
        "FSKL"
    ],
    "physician": [
        "[fi,zish,uhn]",
        "FSSN"
    ],
    "physics": [
        "[fiz,iks]",
        "FSKS"
    ],
    "physique": [
        "[fi,zeek]",
        "FSK"
    ],
    "pi": [
        "['pahy']",
        "P"
    ],
    "pi'erre": [
        [
            "pee",
            "air"
        ],
        "PR"
    ],
    "piano": [
        "['pee', 'an', 'oh']",
        "PN"
    ],
    "pic": [
        "['pik']",
        "PK"
    ],
    "picasso": [
        "['pi', 'kah', 'soh']",
        "PKS"
    ],
    "pick": [
        "['pik']",
        "PK"
    ],
    "picked": [
        "['pikt']",
        "PKT"
    ],
    "picker": [
        "['pik', 'er']",
        "PKR"
    ],
    "picket": [
        "['pik', 'it']",
        "PKT"
    ],
    "picking": [
        "['pik', 'ing']",
        "PKNK"
    ],
    "pickle": [
        "['pik', 'uhl']",
        "PKL"
    ],
    "pickles": [
        "[pik,uhl,s]",
        "PKLS"
    ],
    "picks": [
        "['pik', 's']",
        "PKS"
    ],
    "picky": [
        "['pik', 'ee']",
        "PK"
    ],
    "picnic": [
        "[pik,nik]",
        "PKNK"
    ],
    "pics": [
        "['pik', 's']",
        "PKS"
    ],
    "picture": [
        "['pik', 'cher']",
        "PKTR"
    ],
    "pictures": [
        "['pik', 'cher', 's']",
        "PKTRS"
    ],
    "pie": [
        "['pahy']",
        "P"
    ],
    "piece": [
        "['pees']",
        "PS"
    ],
    "pieces": [
        "['pees', 's']",
        "PSS"
    ],
    "pied": [
        "[pahyd]",
        "PT"
    ],
    "pier": [
        "['peer']",
        "P"
    ],
    "pierce": [
        "[peers]",
        "PRS"
    ],
    "pierced": [
        "[peerst]",
        "PRST"
    ],
    "piercing": [
        "[peer,sing]",
        "PRSNK"
    ],
    "pierre": [
        "['peerfor1pee']",
        "PR"
    ],
    "pies": [
        "['pahyz']",
        "PS"
    ],
    "pig": [
        "['pig']",
        "PK"
    ],
    "pigeon": [
        "['pij', 'uhn']",
        "PJN"
    ],
    "pigeons": [
        "['pij', 'uhn', 's']",
        "PJNS"
    ],
    "piggy": [
        "['pig', 'ee']",
        "PK"
    ],
    "pigment": [
        "[pig,muhnt]",
        "PKMNT"
    ],
    "pigs": [
        "['pigz']",
        "PKS"
    ],
    "pilates": [
        "[pi,lah,teez]",
        "PLTS"
    ],
    "pile": [
        "['pahyl']",
        "PL"
    ],
    "piles": [
        "['pahyl', 's']",
        "PLS"
    ],
    "pilgrim": [
        "['pil', 'grim']",
        "PLKRM"
    ],
    "pilgrims": [
        "['pil', 'grim', 's']",
        "PLKRMS"
    ],
    "piling": [
        "['pahy', 'ling']",
        "PLNK"
    ],
    "pill": [
        "['pil']",
        "PL"
    ],
    "pillar": [
        "['pil', 'er']",
        "PLR"
    ],
    "pillars": [
        "[pil,er,s]",
        "PLRS"
    ],
    "pillow": [
        "['pil', 'oh']",
        "PL"
    ],
    "pillowcase": [
        "[pil,oh,keys]",
        "PLKS"
    ],
    "pillows": [
        "['pil', 'oh', 's']",
        "PLS"
    ],
    "pills": [
        "['pil', 's']",
        "PLS"
    ],
    "pillsbury": [
        "['pilz', 'ber', 'ee']",
        "PLSPR"
    ],
    "pilot": [
        "['pahy', 'luht']",
        "PLT"
    ],
    "pilots": [
        "['pahy', 'luht', 's']",
        "PLTS"
    ],
    "pimp": [
        "['pimp']",
        "PMP"
    ],
    "pimped": [
        "[pimp,ed]",
        "PMPT"
    ],
    "pimping": [
        "['pim', 'ping']",
        "PMPNK"
    ],
    "pimple": [
        "['pim', 'puhl']",
        "PMPL"
    ],
    "pimples": [
        "[pim,puhl,s]",
        "PMPLS"
    ],
    "pimps": [
        "['pimp', 's']",
        "PMPS"
    ],
    "pinch": [
        "[pinch]",
        "PNX"
    ],
    "pinched": [
        "[pinch,ed]",
        "PNXT"
    ],
    "pinching": [
        "['pinch', 'ing']",
        "PNXNK"
    ],
    "pine": [
        "[pahyn]",
        "PN"
    ],
    "pineapple": [
        "['pahy', 'nap', 'uhl']",
        "PNPL"
    ],
    "ping": [
        "['ping']",
        "PNK"
    ],
    "pink": [
        "['pingk']",
        "PNK"
    ],
    "pinker": [
        "['pingk', 'er']",
        "PNKR"
    ],
    "pinkie": [
        "['ping', 'kee']",
        "PNK"
    ],
    "pinkies": [
        "[ping,kee,s]",
        "PNKS"
    ],
    "pinky": [
        "['ping', 'kee']",
        "PNK"
    ],
    "pinky's": [
        "[ping,kee,'s]",
        "PNKS"
    ],
    "pinned": [
        "[pin,ned]",
        "PNT"
    ],
    "pinocchio": [
        "['pi', 'noh', 'kee', 'oh']",
        "PNX"
    ],
    "pinot": [
        "[pee,noh]",
        "PNT"
    ],
    "pins": [
        "[pinz]",
        "PNS"
    ],
    "pint": [
        "['pahynt']",
        "PNT"
    ],
    "pinto": [
        "['pin', 'toh']",
        "PNT"
    ],
    "pints": [
        "['pahynt', 's']",
        "PNTS"
    ],
    "pioneer": [
        "[pahy,uh,neer]",
        "PNR"
    ],
    "pious": [
        "[pahy,uhs]",
        "PS"
    ],
    "pipe": [
        "['pahyp']",
        "PP"
    ],
    "piped": [
        "['pahyp', 'd']",
        "PPT"
    ],
    "piper": [
        "['pahy', 'per']",
        "PPR"
    ],
    "pipes": [
        "[pahyp,s]",
        "PPS"
    ],
    "piping": [
        "['pahy', 'ping']",
        "PPNK"
    ],
    "pips": [
        "[pip,s]",
        "PPS"
    ],
    "piranha": [
        "[pi,rahn,yuh]",
        "PRN"
    ],
    "piranhas": [
        "['pi', 'rahn', 'yuh', 's']",
        "PRNS"
    ],
    "pirate": [
        "[pahy,ruht]",
        "PRT"
    ],
    "pisa": [
        "[pee,zuh]",
        "PS"
    ],
    "pisces": [
        "[pahy,seez]",
        "PSS"
    ],
    "piss": [
        "['pis']",
        "PS"
    ],
    "pissed": [
        "['pist']",
        "PST"
    ],
    "pissing": [
        "['pis', 'ing']",
        "PSNK"
    ],
    "pissy": [
        "['pis', 'ee']",
        "PS"
    ],
    "pistol": [
        "['pis', 'tl']",
        "PSTL"
    ],
    "pistol's": [
        "[pis,tl,'s]",
        "PSTLLS"
    ],
    "pistols": [
        "['pis', 'tl', 's']",
        "PSTLS"
    ],
    "piston": [
        "[pis,tuhn]",
        "PSTN"
    ],
    "pistons": [
        "['pis', 'tuhn', 's']",
        "PSTNS"
    ],
    "pit": [
        "['pit']",
        "PT"
    ],
    "pita": [
        "[pee,tuh]",
        "PT"
    ],
    "pitch": [
        "['pich']",
        "PX"
    ],
    "pitcher": [
        "[pich,er]",
        "PXR"
    ],
    "pitchfork": [
        "['pich', 'fawrk']",
        "PXFRK"
    ],
    "pitching": [
        "['pich', 'ing']",
        "PXNK"
    ],
    "pitiful": [
        "['pit', 'i', 'fuhl']",
        "PTFL"
    ],
    "pits": [
        "[pit,s]",
        "PTS"
    ],
    "pitt": [
        "[pit]",
        "PT"
    ],
    "pittsburgh": [
        "[pits,burg]",
        "PTSPRK"
    ],
    "pity": [
        "['pit', 'ee']",
        "PT"
    ],
    "pivot": [
        "['piv', 'uht']",
        "PFT"
    ],
    "pizza": [
        "['peet', 'suh']",
        "PS"
    ],
    "pi\u00f1a": [
        "['pee', 'nyah']",
        "PN"
    ],
    "pi\u00f1ata": [
        "['peen', 'yah', 'tuh']",
        "PNT"
    ],
    "place": [
        "['pleys']",
        "PLS"
    ],
    "placed": [
        "[pleys,d]",
        "PLST"
    ],
    "placement": [
        "[pleys,muhnt]",
        "PLSMNT"
    ],
    "places": [
        "['pleys', 's']",
        "PLSS"
    ],
    "plaid": [
        "[plad]",
        "PLT"
    ],
    "plain": [
        "['pleyn']",
        "PLN"
    ],
    "plaintiff": [
        "[pleyn,tif]",
        "PLNTF"
    ],
    "plan": [
        "['plan']",
        "PLN"
    ],
    "plane": [
        "['pleyn']",
        "PLN"
    ],
    "planes": [
        "['pleyn', 's']",
        "PLNS"
    ],
    "planet": [
        "['plan', 'it']",
        "PLNT"
    ],
    "plank": [
        "['plangk']",
        "PLNK"
    ],
    "planking": [
        "[plang,king]",
        "PLNKNK"
    ],
    "planks": [
        "['plangk', 's']",
        "PLNKS"
    ],
    "planned": [
        "['pland']",
        "PLNT"
    ],
    "planning": [
        "['plan', 'ing']",
        "PLNNK"
    ],
    "plans": [
        "['plan', 's']",
        "PLNS"
    ],
    "plant": [
        "['plant']",
        "PLNT"
    ],
    "planted": [
        "[plant,ed]",
        "PLNTT"
    ],
    "planters": [
        "[plan,ter,s]",
        "PLNTRS"
    ],
    "planting": [
        "[plant,ing]",
        "PLNTNK"
    ],
    "plants": [
        "['plant', 's']",
        "PLNTS"
    ],
    "plaque": [
        "['plak']",
        "PLK"
    ],
    "plaques": [
        "['plak', 's']",
        "PLKS"
    ],
    "plasma": [
        "[plaz,muh]",
        "PLSM"
    ],
    "plastered": [
        "[plas,terd]",
        "PLSTRT"
    ],
    "plastic": [
        "['plas', 'tik']",
        "PLSTK"
    ],
    "plat": [
        "[plat]",
        "PLT"
    ],
    "plate": [
        "['pleyt']",
        "PLT"
    ],
    "plateau": [
        "[pla,tohor]",
        "PLT"
    ],
    "plated": [
        "[pley,tid]",
        "PLTT"
    ],
    "plates": [
        "['pleyt', 's']",
        "PLTS"
    ],
    "platinum": [
        "['plat', 'n', 'uhm']",
        "PLTNM"
    ],
    "plats": [
        "[plat,s]",
        "PLTS"
    ],
    "platter": [
        "['plat', 'er']",
        "PLTR"
    ],
    "play": [
        "['pley']",
        "PL"
    ],
    "playboy": [
        "['pley', 'boi']",
        "PLP"
    ],
    "playboy's": [
        "[pley,boi,'s]",
        "PLPS"
    ],
    "played": [
        "['pley', 'ed']",
        "PLT"
    ],
    "player": [
        "['pley', 'er']",
        "PLR"
    ],
    "player's": [
        "[pley,er,'s]",
        "PLRRS"
    ],
    "players": [
        "['pley', 'er', 's']",
        "PLRS"
    ],
    "playground": [
        "['pley', 'ground']",
        "PLKRNT"
    ],
    "playgrounds": [
        "['pley', 'ground', 's']",
        "PLKRNTS"
    ],
    "playing": [
        "['pley', 'ing']",
        "PLNK"
    ],
    "playlist": [
        "[pley,list]",
        "PLLST"
    ],
    "plays": [
        "['pley', 's']",
        "PLS"
    ],
    "plaza": [
        "['plah', 'zuh']",
        "PLS"
    ],
    "plea": [
        "[plee]",
        "PL"
    ],
    "plead": [
        "['pleed']",
        "PLT"
    ],
    "pleading": [
        "[plee,ding]",
        "PLTNK"
    ],
    "pleasant": [
        "[plez,uhnt]",
        "PLSNT"
    ],
    "please": [
        "['pleez']",
        "PLS"
    ],
    "pleased": [
        "['pleez', 'd']",
        "PLST"
    ],
    "pleaser": [
        "['pleez', 'r']",
        "PLSR"
    ],
    "pleasing": [
        "[plee,zing]",
        "PLSNK"
    ],
    "pleasure": [
        "['plezh', 'er']",
        "PLSR"
    ],
    "pleasures": [
        "[plezh,er,s]",
        "PLSRS"
    ],
    "pledge": [
        "[plej]",
        "PLJ"
    ],
    "plenty": [
        "['plen', 'tee']",
        "PLNT"
    ],
    "plot": [
        "['plot']",
        "PLT"
    ],
    "plotted": [
        "[plot,ted]",
        "PLTT"
    ],
    "plotting": [
        "['plot', 'ting']",
        "PLTNK"
    ],
    "pluck": [
        "[pluhk]",
        "PLK"
    ],
    "plucked": [
        "['pluhk', 'ed']",
        "PLKT"
    ],
    "plug": [
        "['pluhg']",
        "PLK"
    ],
    "plugged": [
        "['pluhg', 'ged']",
        "PLKT"
    ],
    "plugging": [
        "[pluhg,ging]",
        "PLKNK"
    ],
    "plugs": [
        "[pluhg,s]",
        "PLKS"
    ],
    "plum": [
        "[pluhm]",
        "PLM"
    ],
    "plumber": [
        "[pluhm,er]",
        "PLMPR"
    ],
    "plummer": [
        "[pluhm,mer]",
        "PLMR"
    ],
    "plump": [
        "[pluhmp]",
        "PLMP"
    ],
    "plunger": [
        "[pluhn,jer]",
        "PLNKR"
    ],
    "plural": [
        "['ploor', 'uhl']",
        "PLRL"
    ],
    "plus": [
        "['pluhs']",
        "PLS"
    ],
    "plush": [
        "['pluhsh']",
        "PLX"
    ],
    "pluto": [
        "['ploo', 'toh']",
        "PLT"
    ],
    "pm": [
        "[pr,mth,m]",
        "PM"
    ],
    "pms": [
        "[(pee,em,es)]",
        "PMS"
    ],
    "pneumonia": [
        "['noo', 'mohn', 'yuh']",
        "NMN"
    ],
    "po": [
        "['poh']",
        "P"
    ],
    "po's": [
        "[poh,'s]",
        "PS"
    ],
    "pocket": [
        "['pok', 'it']",
        "PKT"
    ],
    "pocket's": [
        "['pok', 'it', \"'s\"]",
        "PKTTS"
    ],
    "pocketbook": [
        "[pok,it,book]",
        "PKTPK"
    ],
    "pockets": [
        "['pok', 'it', 's']",
        "PKTS"
    ],
    "podium": [
        "['poh', 'dee', 'uhm']",
        "PTM"
    ],
    "poems": [
        "[poh,uhm,s]",
        "PMS"
    ],
    "poet": [
        "['poh', 'it']",
        "PT"
    ],
    "poetry": [
        "[poh,i,tree]",
        "PTR"
    ],
    "pogo": [
        "['poh', 'goh']",
        "PK"
    ],
    "point": [
        "['point']",
        "PNT"
    ],
    "pointed": [
        "['poin', 'tid']",
        "PNTT"
    ],
    "pointers": [
        "['poin', 'ter', 's']",
        "PNTRS"
    ],
    "pointing": [
        "['poin', 'ting']",
        "PNTNK"
    ],
    "pointless": [
        "[point,lis]",
        "PNTLS"
    ],
    "points": [
        "['point', 's']",
        "PNTS"
    ],
    "poison": [
        "['poi', 'zuhn']",
        "PSN"
    ],
    "poisoned": [
        "[poi,zuhn,ed]",
        "PSNT"
    ],
    "poke": [
        "['pohk']",
        "PK"
    ],
    "poked": [
        "['pohk', 'd']",
        "PKT"
    ],
    "poker": [
        "['poh', 'ker']",
        "PKR"
    ],
    "pokey": [
        "[poh,kee]",
        "PK"
    ],
    "poland": [
        "['poh', 'luhnd']",
        "PLNT"
    ],
    "polar": [
        "['poh', 'ler']",
        "PLR"
    ],
    "polaroid": [
        "['poh', 'luh', 'roid']",
        "PLRT"
    ],
    "pole": [
        "['pohl']",
        "PL"
    ],
    "poler": [
        "[poh,ler]",
        "PLR"
    ],
    "poles": [
        "['pohl', 's']",
        "PLS"
    ],
    "police": [
        "['puh', 'lees']",
        "PLS"
    ],
    "polices": [
        "[puh,lees,s]",
        "PLSS"
    ],
    "policy": [
        "[pol,uh,see]",
        "PLS"
    ],
    "polish": [
        "['pol', 'ish']",
        "PLX"
    ],
    "polished": [
        "[pol,isht]",
        "PLXT"
    ],
    "polite": [
        "[puh,lahyt]",
        "PLT"
    ],
    "politely": [
        "['puh', 'lahyt', 'ly']",
        "PLTL"
    ],
    "politic": [
        "[pol,i,tik]",
        "PLTK"
    ],
    "political": [
        "[puh,lit,i,kuhl]",
        "PLTKL"
    ],
    "politically": [
        "[puh,lit,i,kuhl,ly]",
        "PLTKL"
    ],
    "politician": [
        "['pol', 'i', 'tish', 'uhn']",
        "PLTSN"
    ],
    "politicians": [
        "['pol', 'i', 'tish', 'uhn', 's']",
        "PLTSNS"
    ],
    "politics": [
        "[pol,i,tiks]",
        "PLTKS"
    ],
    "polka": [
        "[pohl,kuh]",
        "PLK"
    ],
    "pollution": [
        "['puh', 'loo', 'shuhn']",
        "PLXN"
    ],
    "polo": [
        "['poh', 'loh']",
        "PL"
    ],
    "polos": [
        "['pol', 'os']",
        "PLS"
    ],
    "pom": [
        "['pom']",
        "PM"
    ],
    "poms": [
        "['pom', 's']",
        "PMS"
    ],
    "ponder": [
        "[pon,der]",
        "PNTR"
    ],
    "pong": [
        "['pong']",
        "PNK"
    ],
    "pony": [
        "[poh,nee]",
        "PN"
    ],
    "ponytail": [
        "[poh,nee,teyl]",
        "PNTL"
    ],
    "poodles": [
        "[pood,l,s]",
        "PTLS"
    ],
    "poof": [
        "['poof']",
        "PF"
    ],
    "pookie": [
        [
            "poh",
            "oh",
            "kee"
        ],
        "PK"
    ],
    "pool": [
        "['pool']",
        "PL"
    ],
    "pools": [
        "[pool,s]",
        "PLS"
    ],
    "poon": [
        "[poon]",
        "PN"
    ],
    "poop": [
        "['poop']",
        "PP"
    ],
    "poor": [
        "['poor']",
        "PR"
    ],
    "poorer": [
        "[poor,er]",
        "PRR"
    ],
    "pop": [
        "['pop']",
        "PP"
    ],
    "pop's": [
        "[pop,'s]",
        "PPPS"
    ],
    "popcorn": [
        "[pop,kawrn]",
        "PPKRN"
    ],
    "pope": [
        "['pohp']",
        "PP"
    ],
    "popped": [
        "['pop', 'ped']",
        "PPT"
    ],
    "popper": [
        "['pop', 'er']",
        "PPR"
    ],
    "poppers": [
        "['pop', 'er', 's']",
        "PPRS"
    ],
    "popping": [
        "['pop', 'ping']",
        "PPNK"
    ],
    "poppy": [
        "[pop,ee]",
        "PP"
    ],
    "pops": [
        "['pops']",
        "PPS"
    ],
    "popsicle": [
        "[pop,si,kuhl]",
        "PPSKL"
    ],
    "popular": [
        "['pop', 'yuh', 'ler']",
        "PPLR"
    ],
    "population": [
        "[pop,yuh,ley,shuhn]",
        "PPLXN"
    ],
    "porcelain": [
        "['pawr', 'suh', 'lin']",
        "PRSLN"
    ],
    "porch": [
        "['pawrch']",
        "PRX"
    ],
    "porches": [
        "[pawrch,es]",
        "PRKS"
    ],
    "porcupine": [
        "[pawr,kyuh,pahyn]",
        "PRKPN"
    ],
    "porcupines": [
        "[pawr,kyuh,pahyn,s]",
        "PRKPNS"
    ],
    "pores": [
        "[pawr,s]",
        "PRS"
    ],
    "pork": [
        "['pawrk']",
        "PRK"
    ],
    "porn": [
        "['pawrn']",
        "PRN"
    ],
    "porno": [
        "['pawrn', 'o']",
        "PRN"
    ],
    "pornography": [
        "[pawr,nog,ruh,fee]",
        "PRNKRF"
    ],
    "pornstar": [
        [
            "pawrn",
            "stahr"
        ],
        "PRNSTR"
    ],
    "porridge": [
        "['pawr', 'ij']",
        "PRJ"
    ],
    "porsches": [
        [
            "pawr",
            "shuh"
        ],
        "PRXS"
    ],
    "port": [
        "['pawrt']",
        "PRT"
    ],
    "porta": [
        "['(prt)']",
        "PRT"
    ],
    "portal": [
        "['pawr', 'tl']",
        "PRTL"
    ],
    "porter": [
        "[pawr,ter]",
        "PRTR"
    ],
    "portion": [
        "[pawr,shuhn]",
        "PRXN"
    ],
    "portland": [
        "['pawrt', 'luhnd']",
        "PRTLNT"
    ],
    "portrait": [
        "['pawr', 'trit']",
        "PRTRT"
    ],
    "portraits": [
        "['pawr', 'trit', 's']",
        "PRTRTS"
    ],
    "portray": [
        "[pawr,trey]",
        "PRTR"
    ],
    "ports": [
        "[pawrt,s]",
        "PRTS"
    ],
    "pose": [
        "['pohz']",
        "PS"
    ],
    "posed": [
        "['pohz', 'd']",
        "PST"
    ],
    "poser": [
        "[poh,zer]",
        "PSR"
    ],
    "posers": [
        "[poh,zer,s]",
        "PSRS"
    ],
    "posing": [
        [
            "poh",
            "sing"
        ],
        "PSNK"
    ],
    "position": [
        "['puh', 'zish', 'uhn']",
        "PSXN"
    ],
    "positions": [
        "['puh', 'zish', 'uhn', 's']",
        "PSXNS"
    ],
    "positive": [
        "['poz', 'i', 'tiv']",
        "PSTF"
    ],
    "positively": [
        "[poz,i,tiv,leeorespeciallyfor3]",
        "PSTFL"
    ],
    "posse": [
        "['pos', 'ee']",
        "PS"
    ],
    "possess": [
        "['puh', 'zes']",
        "PSS"
    ],
    "possessed": [
        "[puh,zest]",
        "PSST"
    ],
    "possession": [
        "['puh', 'zesh', 'uhn']",
        "PSSN"
    ],
    "possessive": [
        "['puh', 'zes', 'iv']",
        "PSSF"
    ],
    "possible": [
        "['pos', 'uh', 'buhl']",
        "PSPL"
    ],
    "possibly": [
        "[pos,uh,blee]",
        "PSPL"
    ],
    "possum": [
        "[pos,uhm]",
        "PSM"
    ],
    "post": [
        "['pohst']",
        "PST"
    ],
    "postal": [
        "[pohs,tl]",
        "PSTL"
    ],
    "postcard": [
        "[pohst,kahrd]",
        "PSTKRT"
    ],
    "posted": [
        "['pohst', 'ed']",
        "PSTT"
    ],
    "poster": [
        "['poh', 'ster']",
        "PSTR"
    ],
    "posters": [
        "['poh', 'ster', 's']",
        "PSTRS"
    ],
    "posting": [
        "['poh', 'sting']",
        "PSTNK"
    ],
    "postman": [
        "[pohst,muhn]",
        "PSTMN"
    ],
    "posture": [
        "['pos', 'cher']",
        "PSTR"
    ],
    "pot": [
        "['pot']",
        "PT"
    ],
    "potato": [
        "['puh', 'tey', 'toh']",
        "PTT"
    ],
    "potatoes": [
        "['puh', 'tey', 'toh', 'es']",
        "PTTS"
    ],
    "potent": [
        "['poht', 'nt']",
        "PTNT"
    ],
    "potential": [
        "[puh,ten,shuhl]",
        "PTNXL"
    ],
    "pothole": [
        "['pot', 'hohl']",
        "P0L"
    ],
    "potholes": [
        "[pot,hohl,s]",
        "P0LS"
    ],
    "potion": [
        "[poh,shuhn]",
        "PXN"
    ],
    "pots": [
        "['pot', 's']",
        "PTS"
    ],
    "potter": [
        "[pot,er]",
        "PTR"
    ],
    "potty": [
        "['pot', 'ee']",
        "PT"
    ],
    "pouch": [
        "['pouch']",
        "PX"
    ],
    "pound": [
        "['pound']",
        "PNT"
    ],
    "pounding": [
        "[pound,ing]",
        "PNTNK"
    ],
    "pounds": [
        "['pound', 's']",
        "PNTS"
    ],
    "pour": [
        "['pawr']",
        "PR"
    ],
    "poured": [
        "['pawr', 'ed']",
        "PRT"
    ],
    "pouring": [
        "['pawr', 'ing']",
        "PRNK"
    ],
    "pours": [
        "[pawr,s]",
        "PRS"
    ],
    "pout": [
        "[pout]",
        "PT"
    ],
    "pouting": [
        "['pout', 'ing']",
        "PTNK"
    ],
    "poverty": [
        "['pov', 'er', 'tee']",
        "PFRT"
    ],
    "pow": [
        "['pou']",
        "P"
    ],
    "powder": [
        "['pou', 'der']",
        "PTR"
    ],
    "power": [
        "['pou', 'er']",
        "PR"
    ],
    "powerful": [
        "['pou', 'er', 'fuhl']",
        "PRFL"
    ],
    "powers": [
        "['pou', 'erz']",
        "PRS"
    ],
    "practically": [
        "[prak,tik,lee]",
        "PRKTKL"
    ],
    "practice": [
        "['prak', 'tis']",
        "PRKTS"
    ],
    "practicing": [
        "[prak,ti,sing]",
        "PRKTSNK"
    ],
    "praise": [
        "[preyz]",
        "PRS"
    ],
    "praises": [
        "[preyz,s]",
        "PRSS"
    ],
    "prancer": [
        "[prans,r]",
        "PRNSR"
    ],
    "pray": [
        "['prey']",
        "PR"
    ],
    "prayed": [
        "['prey', 'ed']",
        "PRT"
    ],
    "prayer": [
        "['prair']",
        "PRR"
    ],
    "prayers": [
        "['prair', 's']",
        "PRRS"
    ],
    "praying": [
        "['prey', 'ing']",
        "PRNK"
    ],
    "preach": [
        "['preech']",
        "PRX"
    ],
    "preacher": [
        "['pree', 'cher']",
        "PRXR"
    ],
    "preachers": [
        "['pree', 'cher', 's']",
        "PRXRS"
    ],
    "preaching": [
        "['pree', 'ching']",
        "PRXNK"
    ],
    "precinct": [
        "[pree,singkt]",
        "PRSNKT"
    ],
    "precious": [
        "['presh', 'uhs']",
        "PRSS"
    ],
    "precise": [
        "['pri', 'sahys']",
        "PRSS"
    ],
    "precision": [
        "['pri', 'sizh', 'uhn']",
        "PRSSN"
    ],
    "predator": [
        "['pred', 'uh', 'ter']",
        "PRTTR"
    ],
    "predicament": [
        "['pri', 'dik', 'uh', 'muhntfor1']",
        "PRTKMNT"
    ],
    "predicate": [
        "['verbpred', 'i', 'keyt']",
        "PRTKT"
    ],
    "predict": [
        "[pri,dikt]",
        "PRTKT"
    ],
    "predicted": [
        "['pri', 'dikt', 'ed']",
        "PRTKTT"
    ],
    "prefer": [
        "['pri', 'fur']",
        "PRFR"
    ],
    "preference": [
        "[pref,er,uhns]",
        "PRFRNS"
    ],
    "pregnant": [
        "['preg', 'nuhnt']",
        "PRNNT"
    ],
    "premature": [
        "[pree,muh,choor]",
        "PRMTR"
    ],
    "premeditated": [
        "[pri,med,i,tey,tid]",
        "PRMTTTT"
    ],
    "premier": [
        "[pri,meer]",
        "PRM"
    ],
    "premium": [
        "[pree,mee,uhm]",
        "PRMM"
    ],
    "prepare": [
        "['pri', 'pair']",
        "PRPR"
    ],
    "prepared": [
        "[pri,paird]",
        "PRPRT"
    ],
    "prescribe": [
        "[pri,skrahyb]",
        "PRSKP"
    ],
    "prescription": [
        "['pri', 'skrip', 'shuhn']",
        "PRSKPXN"
    ],
    "prescriptions": [
        "['pri', 'skrip', 'shuhn', 's']",
        "PRSKPXNS"
    ],
    "presence": [
        "['prez', 'uhns']",
        "PRSNS"
    ],
    "present": [
        "[prez,uhnt]",
        "PRSNT"
    ],
    "presents": [
        "[prez,uhnt,s]",
        "PRSNTS"
    ],
    "president": [
        "['prez', 'i', 'duhnt']",
        "PRSTNT"
    ],
    "presidential": [
        "['prez', 'i', 'den', 'shuhl']",
        "PRSTNXL"
    ],
    "presidents": [
        "['prez', 'i', 'duhnt', 's']",
        "PRSTNTS"
    ],
    "press": [
        "['pres']",
        "PRS"
    ],
    "pressed": [
        "['pres', 'ed']",
        "PRST"
    ],
    "pressing": [
        "['pres', 'ing']",
        "PRSNK"
    ],
    "pressure": [
        "['presh', 'er']",
        "PRSR"
    ],
    "prestigious": [
        "['pre', 'stij', 'uhs']",
        "PRSTJS"
    ],
    "pretend": [
        "['pri', 'tend']",
        "PRTNT"
    ],
    "pretended": [
        "['pri', 'ten', 'did']",
        "PRTNTT"
    ],
    "pretender": [
        "['pri', 'ten', 'der']",
        "PRTNTR"
    ],
    "pretending": [
        "['pri', 'tend', 'ing']",
        "PRTNTNK"
    ],
    "pretty": [
        "['prit', 'ee']",
        "PRT"
    ],
    "prevail": [
        "[pri,veyl]",
        "PRFL"
    ],
    "prevent": [
        "[pri,vent]",
        "PRFNT"
    ],
    "preview": [
        "[pree,vyoo]",
        "PRF"
    ],
    "previous": [
        "[pree,vee,uhs]",
        "PRFS"
    ],
    "prey": [
        "['prey']",
        "PR"
    ],
    "price": [
        "['prahys']",
        "PRS"
    ],
    "priceless": [
        "['prahys', 'lis']",
        "PRSLS"
    ],
    "prices": [
        "['prahys', 's']",
        "PRSS"
    ],
    "prick": [
        "['prik']",
        "PRK"
    ],
    "pricks": [
        "[prik,s]",
        "PRKS"
    ],
    "pride": [
        "['prahyd']",
        "PRT"
    ],
    "priest": [
        "[preest]",
        "PRST"
    ],
    "prima": [
        "[pree,mahin,terpah,res,]",
        "PRM"
    ],
    "prime": [
        "[prahym]",
        "PRM"
    ],
    "primo": [
        "[pree,moh]",
        "PRM"
    ],
    "prince": [
        "['prins']",
        "PRNS"
    ],
    "princess": [
        "[prin,sis]",
        "PRNSS"
    ],
    "principal": [
        "['prin', 'suh', 'puhl']",
        "PRNSPL"
    ],
    "principle": [
        "[prin,suh,puhl]",
        "PRNSPL"
    ],
    "principles": [
        "[prin,suh,puhl,s]",
        "PRNSPLS"
    ],
    "print": [
        "['print']",
        "PRNT"
    ],
    "printed": [
        "[print,ed]",
        "PRNTT"
    ],
    "printing": [
        "[prin,ting]",
        "PRNTNK"
    ],
    "prints": [
        "['print', 's']",
        "PRNTS"
    ],
    "prior": [
        "[prahy,er]",
        "PRR"
    ],
    "priority": [
        "[prahy,awr,i,tee]",
        "PRRT"
    ],
    "prison": [
        "['priz', 'uhn']",
        "PRSN"
    ],
    "prisoner": [
        "['priz', 'uh', 'ner']",
        "PRSNR"
    ],
    "prisoners": [
        "[priz,uh,ner,s]",
        "PRSNRS"
    ],
    "prisons": [
        "[priz,uhn,s]",
        "PRSNS"
    ],
    "prissy": [
        "[pris,ee]",
        "PRS"
    ],
    "privacy": [
        "['prahy', 'vuh', 'see']",
        "PRFS"
    ],
    "private": [
        "['prahy', 'vit']",
        "PRFT"
    ],
    "privates": [
        "['prahy', 'vit', 's']",
        "PRFTS"
    ],
    "privilege": [
        "[priv,uh,lij]",
        "PRFLJ"
    ],
    "prize": [
        "['prahyz']",
        "PRS"
    ],
    "pro": [
        "['proh']",
        "PR"
    ],
    "prob": [
        "['prob']",
        "PRP"
    ],
    "probably": [
        "['prob', 'uh', 'blee']",
        "PRPPL"
    ],
    "probation": [
        "['proh', 'bey', 'shuhn']",
        "PRPXN"
    ],
    "problem": [
        "['prob', 'luhm']",
        "PRPLM"
    ],
    "problems": [
        "['prob', 'luhm', 's']",
        "PRPLMS"
    ],
    "procedure": [
        "[pruh,see,jer]",
        "PRSTR"
    ],
    "proceed": [
        "['verbpruh', 'seed']",
        "PRST"
    ],
    "process": [
        "['pros', 'es']",
        "PRSS"
    ],
    "prodigy": [
        "[prod,i,jee]",
        "PRTJ"
    ],
    "produce": [
        "['verbpruh', 'doos']",
        "PRTS"
    ],
    "produced": [
        "['verbpruh', 'doos', 'd']",
        "PRTST"
    ],
    "producer": [
        "['pruh', 'doo', 'ser']",
        "PRTSR"
    ],
    "producers": [
        "[pruh,doo,ser,s]",
        "PRTSRS"
    ],
    "product": [
        "['prod', 'uhkt']",
        "PRTKT"
    ],
    "production": [
        "['pruh', 'duhk', 'shuhn']",
        "PRTKXN"
    ],
    "profess": [
        "[pruh,fes]",
        "PRFS"
    ],
    "profession": [
        "[pruh,fesh,uhn]",
        "PRFSN"
    ],
    "professional": [
        "['pruh', 'fesh', 'uh', 'nl']",
        "PRFSNL"
    ],
    "professionals": [
        "[pruh,fesh,uh,nl,s]",
        "PRFSNLS"
    ],
    "professor": [
        "['pruh', 'fes', 'er']",
        "PRFSR"
    ],
    "profile": [
        "['proh', 'fahyl']",
        "PRFL"
    ],
    "profit": [
        "['prof', 'it']",
        "PRFT"
    ],
    "profits": [
        "['prof', 'it', 's']",
        "PRFTS"
    ],
    "profound": [
        "['pruh', 'found']",
        "PRFNT"
    ],
    "program": [
        "[proh,gram]",
        "PRKRM"
    ],
    "progress": [
        "['nounprog', 'res']",
        "PRKRS"
    ],
    "progressing": [
        "[nounprog,res,ing]",
        "PRKRSNK"
    ],
    "progression": [
        "['pruh', 'gresh', 'uhn']",
        "PRKRSN"
    ],
    "project": [
        "['nounproj', 'ekt']",
        "PRJKT"
    ],
    "projectors": [
        "[pruh,jek,ter,s]",
        "PRJKTRS"
    ],
    "projects": [
        "['nounproj', 'ekt', 's']",
        "PRJKTS"
    ],
    "prolong": [
        "[pruh,lawng]",
        "PRLNK"
    ],
    "prom": [
        "['prom']",
        "PRM"
    ],
    "promethazine": [
        "['proh', 'meth', 'uh', 'zeen']",
        "PRM0SN"
    ],
    "promise": [
        "['prom', 'is']",
        "PRMS"
    ],
    "promised": [
        "['prom', 'is', 'd']",
        "PRMST"
    ],
    "promises": [
        "['prom', 'is', 's']",
        "PRMSS"
    ],
    "promising": [
        "[prom,uh,sing]",
        "PRMSNK"
    ],
    "promo": [
        "['proh', 'moh']",
        "PRM"
    ],
    "promote": [
        "['pruh', 'moht']",
        "PRMT"
    ],
    "promoter": [
        "[pruh,moh,ter]",
        "PRMTR"
    ],
    "promoters": [
        "['pruh', 'moh', 'ter', 's']",
        "PRMTRS"
    ],
    "promotion": [
        "[pruh,moh,shuhn]",
        "PRMXN"
    ],
    "promotions": [
        "[pruh,moh,shuhn,s]",
        "PRMXNS"
    ],
    "prone": [
        "[prohn]",
        "PRN"
    ],
    "pronounce": [
        "['pruh', 'nouns']",
        "PRNNS"
    ],
    "pronto": [
        "['pron', 'toh']",
        "PRNT"
    ],
    "proof": [
        "['proof']",
        "PRF"
    ],
    "prop": [
        "['prop']",
        "PRP"
    ],
    "propaganda": [
        "['prop', 'uh', 'gan', 'duh']",
        "PRPKNT"
    ],
    "propane": [
        "['proh', 'peyn']",
        "PRPN"
    ],
    "propellers": [
        "['pruh', 'pel', 'er', 's']",
        "PRPLRS"
    ],
    "proper": [
        "['prop', 'er']",
        "PRPR"
    ],
    "properly": [
        "[prop,er,ly]",
        "PRPRL"
    ],
    "property": [
        "['prop', 'er', 'tee']",
        "PRPRT"
    ],
    "prophecy": [
        "[prof,uh,see]",
        "PRFS"
    ],
    "prophet": [
        "[prof,it]",
        "PRFT"
    ],
    "propose": [
        "['pruh', 'pohz']",
        "PRPS"
    ],
    "props": [
        "[props]",
        "PRPS"
    ],
    "pros": [
        "['proh', 's']",
        "PRS"
    ],
    "prosecutor": [
        "[pros,i,kyoo,ter]",
        "PRSKTR"
    ],
    "prosper": [
        "['pros', 'per']",
        "PRSPR"
    ],
    "prostitute": [
        "[pros,ti,toot]",
        "PRSTTT"
    ],
    "prostitution": [
        "[pros,ti,too,shuhn]",
        "PRSTTXN"
    ],
    "protect": [
        "['pruh', 'tekt']",
        "PRTKT"
    ],
    "protected": [
        "[pruh,tekt,ed]",
        "PRTKTT"
    ],
    "protecting": [
        "[pruh,tek,ting]",
        "PRTKTNK"
    ],
    "protection": [
        "['pruh', 'tek', 'shuhn']",
        "PRTKXN"
    ],
    "prototype": [
        "['proh', 'tuh', 'tahyp']",
        "PRTTP"
    ],
    "proud": [
        "['proud']",
        "PRT"
    ],
    "prove": [
        "['proov']",
        "PRF"
    ],
    "proved": [
        "['proov', 'd']",
        "PRFT"
    ],
    "proven": [
        "[proov,n]",
        "PRFN"
    ],
    "provide": [
        "['pruh', 'vahyd']",
        "PRFT"
    ],
    "provided": [
        "[pruh,vahy,did]",
        "PRFTT"
    ],
    "provider": [
        "[pruh,vahy,der]",
        "PRFTR"
    ],
    "providing": [
        "[pruh,vahy,ding]",
        "PRFTNK"
    ],
    "provoke": [
        "['pruh', 'vohk']",
        "PRFK"
    ],
    "provoked": [
        "[pruh,vohk,d]",
        "PRFKT"
    ],
    "provoking": [
        "[pruh,voh,king]",
        "PRFKNK"
    ],
    "prowl": [
        "[proul]",
        "PRL"
    ],
    "prowler": [
        "[prou,ler]",
        "PRLR"
    ],
    "prozac": [
        "[proh,zak]",
        "PRSK"
    ],
    "pry": [
        "[prahy]",
        "PR"
    ],
    "ps": [
        "['pee']",
        "S"
    ],
    "psyche": [
        "['sahyk']",
        "SX"
    ],
    "psychiatrist": [
        "[si,kahy,uh,trist]",
        "SKTRST"
    ],
    "psychic": [
        "['sahy', 'kik']",
        "SXK"
    ],
    "psycho": [
        "['sahy', 'koh']",
        "SX"
    ],
    "psychopath": [
        "[sahy,kuh,path]",
        "SXP0"
    ],
    "psychopathic": [
        "['sahy', 'kuh', 'path', 'ik']",
        "SXP0K"
    ],
    "pt": [
        "['pltn', 'm']",
        "PT"
    ],
    "pu": [
        "[pl,tn,m]",
        "P"
    ],
    "pub": [
        "['puhb']",
        "PP"
    ],
    "public": [
        "['puhb', 'lik']",
        "PPLK"
    ],
    "publicity": [
        "[puh,blis,i,tee]",
        "PPLST"
    ],
    "publicly": [
        "['puhb', 'lik', 'lee']",
        "PPLKL"
    ],
    "publishing": [
        "[puhb,li,shing]",
        "PPLXNK"
    ],
    "puck": [
        "['puhk']",
        "PK"
    ],
    "pucker": [
        "[puhk,er]",
        "PKR"
    ],
    "pudding": [
        "[pood,ing]",
        "PTNK"
    ],
    "puddle": [
        "[puhd,l]",
        "PTL"
    ],
    "puff": [
        "['puhf']",
        "PF"
    ],
    "puffing": [
        "['puhf', 'ing']",
        "PFNK"
    ],
    "puffs": [
        "['puhf', 's']",
        "PFS"
    ],
    "puffy": [
        "[puhf,ee]",
        "PF"
    ],
    "pull": [
        "['pool']",
        "PL"
    ],
    "pulled": [
        "['poold']",
        "PLT"
    ],
    "pulling": [
        "['pool', 'ing']",
        "PLNK"
    ],
    "pulpit": [
        "['pool', 'pit']",
        "PLPT"
    ],
    "pulse": [
        "['puhls']",
        "PLS"
    ],
    "puma": [
        "[pyoo,muh]",
        "PM"
    ],
    "pumas": [
        "['pyoo', 'muh', 's']",
        "PMS"
    ],
    "pump": [
        "['puhmp']",
        "PMP"
    ],
    "pumped": [
        "[puhmp,ed]",
        "PMPT"
    ],
    "pumping": [
        "['puhm', 'ping']",
        "PMPNK"
    ],
    "pumpkin": [
        "['puhmp', 'kinor']",
        "PMPKN"
    ],
    "pumps": [
        "['puhmp', 's']",
        "PMPS"
    ],
    "pun": [
        "['puhn']",
        "PN"
    ],
    "punch": [
        "['puhnch']",
        "PNX"
    ],
    "punches": [
        "[puhnch,es]",
        "PNXS"
    ],
    "punching": [
        "['puhnch', 'ing']",
        "PNXNK"
    ],
    "punish": [
        "[puhn,ish]",
        "PNX"
    ],
    "punished": [
        "['puhn', 'ish', 'ed']",
        "PNXT"
    ],
    "punishment": [
        "[puhn,ish,muhnt]",
        "PNXMNT"
    ],
    "punk": [
        "['puhngk']",
        "PNK"
    ],
    "punks": [
        "[puhngk,s]",
        "PNKS"
    ],
    "punt": [
        "['puhnt']",
        "PNT"
    ],
    "punting": [
        "['puhnt', 'ing']",
        "PNTNK"
    ],
    "pup": [
        "['puhp']",
        "PP"
    ],
    "pupils": [
        "['pyoo', 'puhl', 's']",
        "PPLS"
    ],
    "puppet": [
        "[puhp,it]",
        "PPT"
    ],
    "puppy": [
        "['puhp', 'ee']",
        "PP"
    ],
    "purchase": [
        "['pur', 'chuhs']",
        "PRXS"
    ],
    "purchased": [
        "['pur', 'chuhs', 'd']",
        "PRXST"
    ],
    "pure": [
        "['pyoor']",
        "PR"
    ],
    "purest": [
        "['pyoor', 'st']",
        "PRST"
    ],
    "purple": [
        "['pur', 'puhl']",
        "PRPL"
    ],
    "purpose": [
        "['pur', 'puhs']",
        "PRPS"
    ],
    "purposely": [
        "[pur,puhs,lee]",
        "PRPSL"
    ],
    "purr": [
        "[pur]",
        "PR"
    ],
    "purse": [
        "['purs']",
        "PRS"
    ],
    "purses": [
        "['purs', 's']",
        "PRSS"
    ],
    "pursue": [
        "['per', 'soo']",
        "PRS"
    ],
    "pursuing": [
        [
            "per",
            "soo",
            "ing"
        ],
        "PRSNK"
    ],
    "pursuit": [
        "[per,soot]",
        "PRST"
    ],
    "push": [
        "['poosh']",
        "PX"
    ],
    "pushed": [
        "['poosh', 'ed']",
        "PXT"
    ],
    "pusher": [
        "['poosh', 'er']",
        "PXR"
    ],
    "pushing": [
        "['poosh', 'ing']",
        "PXNK"
    ],
    "puss": [
        "['poos']",
        "PS"
    ],
    "pussy": [
        "['poos', 'ee']",
        "PS"
    ],
    "pussy's": [
        "['poos', 'ee', \"'s\"]",
        "PSS"
    ],
    "pussycat": [
        "[poos,ee,kat]",
        "PSKT"
    ],
    "put": [
        "['poot']",
        "PT"
    ],
    "puts": [
        "['poot', 's']",
        "PTS"
    ],
    "putt": [
        "[puht]",
        "PT"
    ],
    "putting": [
        "['poot', 'ting']",
        "PTNK"
    ],
    "putty": [
        "[puht,ee]",
        "PT"
    ],
    "puzzle": [
        "[puhz,uhl]",
        "PSL"
    ],
    "pyramid": [
        "['pir', 'uh', 'mid']",
        "PRMT"
    ],
    "pyramids": [
        "[pir,uh,mid,s]",
        "PRMTS"
    ],
    "pyrex": [
        "['pahy', 'reks']",
        "PRKS"
    ],
    "pyro": [
        "['pahy', 'roh']",
        "PR"
    ],
    "python": [
        "['pahy', 'thon']",
        "P0N"
    ],
    "q": [
        "['kyoo', '']",
        "K"
    ],
    "qb": [
        [
            "kyoo",
            "bee"
        ],
        "KP"
    ],
    "quad": [
        "[kwod]",
        "KT"
    ],
    "qualified": [
        "[kwol,uh,fahyd]",
        "KLFT"
    ],
    "quality": [
        "['kwol', 'i', 'tee']",
        "KLT"
    ],
    "quarantine": [
        "['kwawr', 'uhn', 'teen']",
        "KRNTN"
    ],
    "quarter": [
        "['kwawr', 'ter']",
        "KRTR"
    ],
    "quarterback": [
        "['kwawr', 'ter', 'bak']",
        "KRTRPK"
    ],
    "quarters": [
        "['kwawr', 'ter', 's']",
        "KRTRS"
    ],
    "queen": [
        "['kween']",
        "KN"
    ],
    "queens": [
        "['kweenz']",
        "KNS"
    ],
    "queso": [
        [
            "ke",
            "so"
        ],
        "KS"
    ],
    "quest": [
        "[kwest]",
        "KST"
    ],
    "question": [
        "['kwes', 'chuhn']",
        "KSXN"
    ],
    "questioning": [
        "['kwes', 'chuh', 'ning']",
        "KSXNNK"
    ],
    "questions": [
        "['kwes', 'chuhn', 's']",
        "KSXNS"
    ],
    "quick": [
        "['kwik']",
        "KK"
    ],
    "quicker": [
        "['kwik', 'er']",
        "KKR"
    ],
    "quickest": [
        "[kwik,est]",
        "KKST"
    ],
    "quickie": [
        "[kwik,ee]",
        "KK"
    ],
    "quickly": [
        "['kwik', 'lee']",
        "KKL"
    ],
    "quickness": [
        "['kwik', 'ness']",
        "KKNS"
    ],
    "quicksand": [
        "[kwik,sand]",
        "KKSNT"
    ],
    "quiet": [
        "['kwahy', 'it']",
        "KT"
    ],
    "quietly": [
        "['kwahy', 'it', 'ly']",
        "KTL"
    ],
    "quincy": [
        "[kwin,zee]",
        "KNS"
    ],
    "quit": [
        "['kwit']",
        "KT"
    ],
    "quite": [
        "['kwahyt']",
        "KT"
    ],
    "quits": [
        "[kwits]",
        "KTS"
    ],
    "quitter": [
        "['kwit', 'er']",
        "KTR"
    ],
    "quitting": [
        "['kwit', 'ting']",
        "KTNK"
    ],
    "quo": [
        "['kwoh']",
        "K"
    ],
    "quota": [
        "['kwoh', 'tuh']",
        "KT"
    ],
    "quote": [
        "[kwoht]",
        "KT"
    ],
    "quoted": [
        "[kwoht,d]",
        "KTT"
    ],
    "quotes": [
        "[kwoht,s]",
        "KTS"
    ],
    "r": [
        "['ahr', '']",
        "R"
    ],
    "rabbit": [
        "['rab', 'it']",
        "RPT"
    ],
    "rabbit's": [
        "[rab,it,'s]",
        "RPTTS"
    ],
    "rabbits": [
        "[rab,it,s]",
        "RPTS"
    ],
    "rabies": [
        "['rey', 'beez']",
        "RPS"
    ],
    "race": [
        "['reys']",
        "RS"
    ],
    "racer": [
        "[rey,ser]",
        "RSR"
    ],
    "races": [
        "['reys', 's']",
        "RSS"
    ],
    "racist": [
        "['rey', 'sist']",
        "RSST"
    ],
    "racists": [
        "['rey', 'sist', 's']",
        "RSSTS"
    ],
    "rack": [
        "['rak']",
        "RK"
    ],
    "racked": [
        "['rak', 'ed']",
        "RKT"
    ],
    "racket": [
        "[rak,it]",
        "RKT"
    ],
    "racking": [
        "['rak', 'ing']",
        "RKNK"
    ],
    "racks": [
        "['rak', 's']",
        "RKS"
    ],
    "rad": [
        "[rad]",
        "RT"
    ],
    "radar": [
        "['rey', 'dahr']",
        "RTR"
    ],
    "radical": [
        "['rad', 'i', 'kuhl']",
        "RTKL"
    ],
    "radio": [
        "['rey', 'dee', 'oh']",
        "RT"
    ],
    "rae": [
        "['rey']",
        "R"
    ],
    "rag": [
        "['rag']",
        "RK"
    ],
    "rage": [
        "['reyj']",
        "RJ"
    ],
    "rags": [
        "['rag', 's']",
        "RKS"
    ],
    "raid": [
        "[reyd]",
        "RT"
    ],
    "raider": [
        "['rey', 'der']",
        "RTR"
    ],
    "rail": [
        "[reyl]",
        "RL"
    ],
    "rain": [
        "['reyn']",
        "RN"
    ],
    "rainbow": [
        "['reyn', 'boh']",
        "RNP"
    ],
    "rainbows": [
        "['reyn', 'boh', 's']",
        "RNPS"
    ],
    "raincoat": [
        "['reyn', 'koht']",
        "RNKT"
    ],
    "raindrops": [
        "[reyn,drop,s]",
        "RNTRPS"
    ],
    "rained": [
        "['reyn', 'ed']",
        "RNT"
    ],
    "raining": [
        "['reyn', 'ing']",
        "RNNK"
    ],
    "rains": [
        "[reyn,s]",
        "RNS"
    ],
    "rainy": [
        "['rey', 'nee']",
        "RN"
    ],
    "raise": [
        "['reyz']",
        "RS"
    ],
    "raised": [
        "['reyzd']",
        "RST"
    ],
    "raising": [
        "[rey,zing]",
        "RSNK"
    ],
    "rake": [
        "['reyk']",
        "RK"
    ],
    "rally": [
        "['ral', 'ee']",
        "RL"
    ],
    "ralo": [
        [
            "rah",
            "loh"
        ],
        "RL"
    ],
    "ram": [
        "['ram']",
        "RM"
    ],
    "ramadan": [
        "[ram,uh,dahn]",
        "RMTN"
    ],
    "rambling": [
        "['ram', 'bling']",
        "RMPLNK"
    ],
    "ramen": [
        "['rah', 'muhn']",
        "RMN"
    ],
    "ramming": [
        "['ram', 'ming']",
        "RMNK"
    ],
    "ramp": [
        "[ramp]",
        "RMP"
    ],
    "rampage": [
        "[nounram,peyj]",
        "RMPJ"
    ],
    "rams": [
        "[ram,s]",
        "RMS"
    ],
    "ran": [
        "['ran']",
        "RN"
    ],
    "ranch": [
        "['ranch']",
        "RNX"
    ],
    "ranchers": [
        "['ran', 'cher', 's']",
        "RNXRS"
    ],
    "random": [
        "['ran', 'duhm']",
        "RNTM"
    ],
    "randomly": [
        "[ran,duhm,ly]",
        "RNTML"
    ],
    "randy": [
        "['ran', 'dee']",
        "RNT"
    ],
    "rang": [
        "[rang]",
        "RNK"
    ],
    "range": [
        "['reynj']",
        "RNJ"
    ],
    "ranger": [
        "['reyn', 'jer']",
        "RNJR"
    ],
    "rank": [
        "['rangk']",
        "RNK"
    ],
    "ranking": [
        "['rang', 'king']",
        "RNKNK"
    ],
    "ranks": [
        "[rangk,s]",
        "RNKS"
    ],
    "ransom": [
        "['ran', 'suhm']",
        "RNSM"
    ],
    "rap": [
        "['rap']",
        "RP"
    ],
    "rap's": [
        "['rap', \"'s\"]",
        "RPPS"
    ],
    "rape": [
        "['reyp']",
        "RP"
    ],
    "raped": [
        "['reyp', 'd']",
        "RPT"
    ],
    "rapid": [
        "['rap', 'id']",
        "RPT"
    ],
    "rapped": [
        "[rap,ped]",
        "RPT"
    ],
    "rapper": [
        "['rap', 'er']",
        "RPR"
    ],
    "rapper's": [
        "[rap,er,'s]",
        "RPRRS"
    ],
    "rappers": [
        "['rap', 'er', 's']",
        "RPRS"
    ],
    "rapping": [
        "['rap', 'ing']",
        "RPNK"
    ],
    "raps": [
        "['rap', 's']",
        "RPS"
    ],
    "rapture": [
        "[rap,cher]",
        "RPTR"
    ],
    "rare": [
        "['rair']",
        "RR"
    ],
    "rarely": [
        "[rair,lee]",
        "RRL"
    ],
    "rari": [
        [
            "ra",
            "ree"
        ],
        "RR"
    ],
    "rash": [
        "['rash']",
        "RX"
    ],
    "rasta": [
        "['ras', 'tuh']",
        "RST"
    ],
    "rastafari": [
        "[ras,tuh,fair,ee]",
        "RSTFR"
    ],
    "rat": [
        "['rat']",
        "RT"
    ],
    "ratchet": [
        "['rach', 'it']",
        "RXT"
    ],
    "ratchets": [
        "[rach,it,s]",
        "RXTS"
    ],
    "rate": [
        "['reyt']",
        "RT"
    ],
    "rate's": [
        "['reyt', \"'s\"]",
        "RTS"
    ],
    "rated": [
        "['reyt', 'd']",
        "RTT"
    ],
    "rates": [
        "[reyt,s]",
        "RTS"
    ],
    "rather": [
        "['adverbrath', 'er']",
        "R0R"
    ],
    "rating": [
        "[rey,ting]",
        "RTNK"
    ],
    "ratio": [
        "['rey', 'shoh']",
        "RT"
    ],
    "rats": [
        "['rat', 's']",
        "RTS"
    ],
    "ratting": [
        "[rat,ting]",
        "RTNK"
    ],
    "rattle": [
        "['rat', 'l']",
        "RTL"
    ],
    "rattling": [
        "[rat,ling]",
        "RTLNK"
    ],
    "raven": [
        "[rey,vuhn]",
        "RFN"
    ],
    "ravioli": [
        "['rav', 'ee', 'oh', 'lee']",
        "RFL"
    ],
    "raw": [
        "['raw']",
        "R"
    ],
    "raws": [
        "[raw,s]",
        "RS"
    ],
    "ray": [
        "['rey']",
        "R"
    ],
    "rays": [
        "['rey', 's']",
        "RS"
    ],
    "razor": [
        "[rey,zer]",
        "RSR"
    ],
    "razors": [
        "[rey,zer,s]",
        "RSRS"
    ],
    "re": [
        "['rey']",
        "R"
    ],
    "reach": [
        "['reech']",
        "RX"
    ],
    "reached": [
        "['reech', 'ed']",
        "RXT"
    ],
    "reaching": [
        "['reech', 'ing']",
        "RXNK"
    ],
    "react": [
        "[ree,akt]",
        "RKT"
    ],
    "reaction": [
        "[ree,ak,shuhn]",
        "RKXN"
    ],
    "read": [
        "['reed']",
        "RT"
    ],
    "reader": [
        "[ree,der]",
        "RTR"
    ],
    "reading": [
        "['ree', 'ding']",
        "RTNK"
    ],
    "ready": [
        "['red', 'ee']",
        "RT"
    ],
    "reagan": [
        "[rey,guhn]",
        "RKN"
    ],
    "real": [
        "['ree', 'uhl']",
        "RL"
    ],
    "realist": [
        "[ree,uh,list]",
        "RLST"
    ],
    "realistic": [
        "[ree,uh,lis,tik]",
        "RLSTK"
    ],
    "reality": [
        "['ree', 'al', 'i', 'tee']",
        "RLT"
    ],
    "realize": [
        "['ree', 'uh', 'lahyz']",
        "RLS"
    ],
    "realized": [
        "['ree', 'uh', 'lahyz', 'd']",
        "RLST"
    ],
    "really": [
        "['ree', 'uh', 'lee']",
        "RL"
    ],
    "realness": [
        "[ree,uhl,ness]",
        "RLNS"
    ],
    "reals": [
        "['ree', 'uhl', 's']",
        "RLS"
    ],
    "realtor": [
        "[ree,uhl,ter]",
        "RLTR"
    ],
    "reap": [
        "['reep']",
        "RP"
    ],
    "reaper": [
        "['ree', 'per']",
        "RPR"
    ],
    "reappear": [
        "[re-,uh,peer]",
        "RPR"
    ],
    "rear": [
        "['reer']",
        "RR"
    ],
    "rearrange": [
        "[re-,uh,reynj]",
        "RRNJ"
    ],
    "reason": [
        "['ree', 'zuhn']",
        "RSN"
    ],
    "reasonable": [
        "[ree,zuh,nuh,buhl]",
        "RSNPL"
    ],
    "reasons": [
        "['ree', 'zuhn', 's']",
        "RSNS"
    ],
    "rebel": [
        "['noun']",
        "RPL"
    ],
    "rebellion": [
        "['ri', 'bel', 'yuhn']",
        "RPLN"
    ],
    "rebellious": [
        "['ri', 'bel', 'yuhs']",
        "RPLS"
    ],
    "rebels": [
        "[noun,s]",
        "RPLS"
    ],
    "rebirth": [
        "['ree', 'burth']",
        "RPR0"
    ],
    "reborn": [
        "[ree,bawrn]",
        "RPRN"
    ],
    "rebound": [
        "['verbri', 'bound']",
        "RPNT"
    ],
    "rebuild": [
        "[ree,bild]",
        "RPLT"
    ],
    "recall": [
        "['verbri', 'kawl']",
        "RKL"
    ],
    "receipt": [
        "[ri,seet]",
        "RSPT"
    ],
    "receipts": [
        "[ri,seet,s]",
        "RSPTS"
    ],
    "receive": [
        "[ri,seev]",
        "RSF"
    ],
    "received": [
        "[ri,seevd]",
        "RSFT"
    ],
    "receiver": [
        "[ri,see,ver]",
        "RSFR"
    ],
    "recent": [
        "['ree', 'suhnt']",
        "RSNT"
    ],
    "recently": [
        "['ree', 'suhnt', 'ly']",
        "RSNTL"
    ],
    "recess": [
        "[ri,ses]",
        "RSS"
    ],
    "recession": [
        "['ri', 'sesh', 'uhn']",
        "RSSN"
    ],
    "recipe": [
        "['res', 'uh', 'pee']",
        "RSP"
    ],
    "recite": [
        "[ri,sahyt]",
        "RST"
    ],
    "reckless": [
        "['rek', 'lis']",
        "RKLS"
    ],
    "reckon": [
        "['rek', 'uhn']",
        "RKN"
    ],
    "reclaim": [
        "[ri,kleym]",
        "RKLM"
    ],
    "recline": [
        "['ri', 'klahyn']",
        "RKLN"
    ],
    "recognition": [
        "[rek,uhg,nish,uhn]",
        "RKNXN"
    ],
    "recognize": [
        "['rek', 'uhg', 'nahyz']",
        "RKNS"
    ],
    "recognized": [
        "['rek', 'uhg', 'nahyz', 'd']",
        "RKNST"
    ],
    "recollect": [
        "[rek,uh,lekt]",
        "RKLKT"
    ],
    "recollection": [
        "[rek,uh,lek,shuhn]",
        "RKLKXN"
    ],
    "recommended": [
        "[rek,uh,mend,ed]",
        "RKMNTT"
    ],
    "reconsider": [
        "['ree', 'kuhn', 'sid', 'er']",
        "RKNSTR"
    ],
    "record": [
        "['verbri', 'kawrd']",
        "RKRT"
    ],
    "recorded": [
        "['verbri', 'kawrd', 'ed']",
        "RKRTT"
    ],
    "recording": [
        "['ri', 'kawr', 'ding']",
        "RKRTNK"
    ],
    "recordings": [
        "[ri,kawr,ding,s]",
        "RKRTNKS"
    ],
    "records": [
        "['verbri', 'kawrd', 's']",
        "RKRTS"
    ],
    "recoup": [
        "[ri,koop]",
        "RKP"
    ],
    "recover": [
        "[ri,kuhv,er]",
        "RKFR"
    ],
    "recovery": [
        "[ri,kuhv,uh,ree]",
        "RKFR"
    ],
    "recruit": [
        "[ri,kroot]",
        "RKRT"
    ],
    "recruiter": [
        "[ri,kroot,er]",
        "RKRTR"
    ],
    "recruiting": [
        "['ri', 'kroot', 'ing']",
        "RKRTNK"
    ],
    "rectum": [
        "[rek,tuhm]",
        "RKTM"
    ],
    "recycle": [
        "['ree', 'sahy', 'kuhl']",
        "RSKL"
    ],
    "red": [
        "['red']",
        "RT"
    ],
    "redbone": [
        "['red', 'bohn']",
        "RTPN"
    ],
    "redbones": [
        "[red,bohn,s]",
        "RTPNS"
    ],
    "redder": [
        "['red', 'der']",
        "RTR"
    ],
    "redeem": [
        "[ri,deem]",
        "RTM"
    ],
    "redefine": [
        "['re-', 'dih', 'fahyn']",
        "RTFN"
    ],
    "redemption": [
        "['ri', 'demp', 'shuhn']",
        "RTMPXN"
    ],
    "redemption's": [
        "[ri,demp,shuhn,'s]",
        "RTMPXNNS"
    ],
    "reduction": [
        "[ri,duhk,shuhn]",
        "RTKXN"
    ],
    "reed": [
        "[reed]",
        "RT"
    ],
    "reef": [
        "['reef']",
        "RF"
    ],
    "reefa": [
        [
            "ree",
            "fah"
        ],
        "RF"
    ],
    "reefer": [
        "['ree', 'fer']",
        "RFR"
    ],
    "reek": [
        "[reek]",
        "RK"
    ],
    "reeking": [
        "[reek,ing]",
        "RKNK"
    ],
    "reel": [
        "[reel]",
        "RL"
    ],
    "reeves": [
        "[reev,s]",
        "RFS"
    ],
    "ref": [
        "['ref']",
        "RF"
    ],
    "refer": [
        "[ri,fur]",
        "RFR"
    ],
    "referee": [
        "['ref', 'uh', 'ree']",
        "RFR"
    ],
    "refill": [
        "[verbree,fil]",
        "RFL"
    ],
    "reflect": [
        "[ri,flekt]",
        "RFLKT"
    ],
    "reflecting": [
        "[ri,flekt,ing]",
        "RFLKTNK"
    ],
    "reflection": [
        "['ri', 'flek', 'shuhn']",
        "RFLKXN"
    ],
    "reflex": [
        "['adjective']",
        "RFLKS"
    ],
    "reflux": [
        "[ree,fluhks]",
        "RFLKS"
    ],
    "refresh": [
        "['ri', 'fresh']",
        "RFRX"
    ],
    "refrigerator": [
        "['ri', 'frij', 'uh', 'rey', 'ter']",
        "RFRJRTR"
    ],
    "refs": [
        "[ref,s]",
        "RFS"
    ],
    "refugee": [
        "['ref', 'yoo', 'jee']",
        "RFJ"
    ],
    "refugees": [
        "[ref,yoo,jee,s]",
        "RFJS"
    ],
    "refund": [
        "['verbri', 'fuhnd']",
        "RFNT"
    ],
    "refusal": [
        "[ri,fyoo,zuhl]",
        "RFSL"
    ],
    "refuse": [
        "['ri', 'fyooz']",
        "RFS"
    ],
    "refused": [
        "[ri,fyooz,d]",
        "RFST"
    ],
    "regal": [
        "['ree', 'guhl']",
        "RKL"
    ],
    "regard": [
        "[ri,gahrd]",
        "RKRT"
    ],
    "regardless": [
        "[ri,gahrd,lis]",
        "RKRTLS"
    ],
    "regime": [
        "[ruh,zheem]",
        "RJM"
    ],
    "register": [
        "[rej,uh,ster]",
        "RJSTR"
    ],
    "registration": [
        "[rej,uh,strey,shuhn]",
        "RJSTRXN"
    ],
    "regret": [
        "['ri', 'gret']",
        "RKRT"
    ],
    "regretful": [
        "[ri,gret,fuhl]",
        "RKRTFL"
    ],
    "regrets": [
        "['ri', 'gret', 's']",
        "RKRTS"
    ],
    "regretting": [
        "[ri,gret,ting]",
        "RKRTNK"
    ],
    "regroup": [
        "[ree,groop]",
        "RKRP"
    ],
    "regular": [
        "['reg', 'yuh', 'ler']",
        "RKLR"
    ],
    "regularly": [
        "[reg,yuh,ler,lee]",
        "RKLRL"
    ],
    "rehab": [
        "['ree', 'hab']",
        "RHP"
    ],
    "rehabilitated": [
        "[ree,huh,bil,i,teyt,d]",
        "RHPLTTT"
    ],
    "rehearse": [
        "[ri,hurs]",
        "RHRS"
    ],
    "reid": [
        "[reed]",
        "RT"
    ],
    "reign": [
        "['reyn']",
        "RN"
    ],
    "reimburse": [
        "[ree,im,burs]",
        "RMPRS"
    ],
    "reincarnated": [
        "['verbree', 'in', 'kahr', 'neyt', 'd']",
        "RNKRNTT"
    ],
    "reindeer": [
        "[reyn,deer]",
        "RNTR"
    ],
    "reins": [
        "[reynz]",
        "RNS"
    ],
    "reinvent": [
        "[ree,in,vent]",
        "RNFNT"
    ],
    "reject": [
        "['verbri', 'jekt']",
        "RJKT"
    ],
    "rejected": [
        "['verbri', 'jekt', 'ed']",
        "RJKTT"
    ],
    "rejection": [
        "[ri,jek,shuhn]",
        "RJKXN"
    ],
    "rejoice": [
        "[ri,jois]",
        "RJS"
    ],
    "relapse": [
        "['verbri', 'laps']",
        "RLPS"
    ],
    "relate": [
        "['ri', 'leyt']",
        "RLT"
    ],
    "related": [
        "['ri', 'ley', 'tid']",
        "RLTT"
    ],
    "relation": [
        "['ri', 'ley', 'shuhn']",
        "RLXN"
    ],
    "relations": [
        "['ri', 'ley', 'shuhn', 's']",
        "RLXNS"
    ],
    "relationship": [
        "['ri', 'ley', 'shuhn', 'ship']",
        "RLXNXP"
    ],
    "relationships": [
        "['ri', 'ley', 'shuhn', 'ship', 's']",
        "RLXNXPS"
    ],
    "relatives": [
        "[rel,uh,tiv,s]",
        "RLTFS"
    ],
    "relax": [
        "['ri', 'laks']",
        "RLKS"
    ],
    "relaxed": [
        "['ri', 'lakst']",
        "RLKST"
    ],
    "relaxing": [
        "['ri', 'laks', 'ing']",
        "RLKSNK"
    ],
    "relay": [
        "['nounree', 'ley']",
        "RL"
    ],
    "release": [
        "['ri', 'lees']",
        "RLS"
    ],
    "relentless": [
        "['ri', 'lent', 'lis']",
        "RLNTLS"
    ],
    "relevant": [
        "['rel', 'uh', 'vuhnt']",
        "RLFNT"
    ],
    "relief": [
        "[ri,leef]",
        "RLF"
    ],
    "relieve": [
        "['ri', 'leev']",
        "RLF"
    ],
    "religion": [
        "['ri', 'lij', 'uhn']",
        "RLJN"
    ],
    "religions": [
        "[ri,lij,uhn,s]",
        "RLJNS"
    ],
    "religious": [
        "['ri', 'lij', 'uhs']",
        "RLJS"
    ],
    "reload": [
        "['re-', 'lohd']",
        "RLT"
    ],
    "reloaded": [
        "[re-ed,lohd]",
        "RLTT"
    ],
    "relocate": [
        "['ree', 'loh', 'keyt']",
        "RLKT"
    ],
    "reluctantly": [
        "[ri,luhk,tuhnt,ly]",
        "RLKTNTL"
    ],
    "rely": [
        "[ri,lahy]",
        "RL"
    ],
    "relying": [
        "[ri,lahy,ing]",
        "RLNK"
    ],
    "remain": [
        "['ri', 'meyn']",
        "RMN"
    ],
    "remained": [
        "[ri,meyn,ed]",
        "RMNT"
    ],
    "remaining": [
        "[ri,meyn,ing]",
        "RMNNK"
    ],
    "remains": [
        "[ri,meyn,s]",
        "RMNS"
    ],
    "remarkable": [
        "['ri', 'mahr', 'kuh', 'buhl']",
        "RMRKPL"
    ],
    "rembrandt": [
        "[rem,brant]",
        "RMPRNT"
    ],
    "remedy": [
        "['rem', 'i', 'dee']",
        "RMT"
    ],
    "remember": [
        "['ri', 'mem', 'ber']",
        "RMMPR"
    ],
    "remembered": [
        "[ri,mem,ber,ed]",
        "RMMPRT"
    ],
    "remembering": [
        "[ri,mem,ber,ing]",
        "RMMPRNK"
    ],
    "remembers": [
        "['ri', 'mem', 'ber', 's']",
        "RMMPRS"
    ],
    "remind": [
        "['ri', 'mahynd']",
        "RMNT"
    ],
    "reminded": [
        "['ri', 'mahynd', 'ed']",
        "RMNTT"
    ],
    "reminder": [
        "[ri,mahyn,der]",
        "RMNTR"
    ],
    "reminders": [
        "[ri,mahyn,der,s]",
        "RMNTRS"
    ],
    "reminding": [
        "['ri', 'mahynd', 'ing']",
        "RMNTNK"
    ],
    "reminds": [
        "['ri', 'mahynd', 's']",
        "RMNTS"
    ],
    "reminisce": [
        "['rem', 'uh', 'nis']",
        "RMNS"
    ],
    "reminiscent": [
        "[rem,uh,nis,uhnt]",
        "RMNSNT"
    ],
    "remix": [
        "['verbree', 'miks']",
        "RMKS"
    ],
    "remorse": [
        "['ri', 'mawrs']",
        "RMRS"
    ],
    "remote": [
        "['ri', 'moht']",
        "RMT"
    ],
    "remove": [
        "['ri', 'moov']",
        "RMF"
    ],
    "removed": [
        "[ri,moovd]",
        "RMFT"
    ],
    "renaissance": [
        "['ren', 'uh', 'sahns']",
        "RNSNS"
    ],
    "renegade": [
        "[ren,i,geyd]",
        "RNKT"
    ],
    "renew": [
        "[ri,noo]",
        "RN"
    ],
    "rent": [
        "['rent']",
        "RNT"
    ],
    "rent's": [
        "['rent', \"'s\"]",
        "RNTTS"
    ],
    "rental": [
        "['ren', 'tl']",
        "RNTL"
    ],
    "rentals": [
        "['ren', 'tl', 's']",
        "RNTLS"
    ],
    "rented": [
        "['rent', 'ed']",
        "RNTT"
    ],
    "renting": [
        "['rent', 'ing']",
        "RNTNK"
    ],
    "rep": [
        "['rep']",
        "RP"
    ],
    "repair": [
        "['ri', 'pair']",
        "RPR"
    ],
    "repay": [
        "['ri', 'pey']",
        "RP"
    ],
    "repeat": [
        "['ri', 'peet']",
        "RPT"
    ],
    "repeatedly": [
        "[ri,pee,tid,ly]",
        "RPTTL"
    ],
    "repeats": [
        "[ri,peet,s]",
        "RPTS"
    ],
    "repent": [
        "['ri', 'pent']",
        "RPNT"
    ],
    "repentance": [
        "[ri,pen,tns]",
        "RPNTNS"
    ],
    "repercussions": [
        "['ree', 'per', 'kuhsh', 'uhn', 's']",
        "RPRKSNS"
    ],
    "repertoire": [
        "[rep,er,twahr]",
        "RPRTR"
    ],
    "repetition": [
        "[rep,i,tish,uhn]",
        "RPTXN"
    ],
    "replace": [
        "['ri', 'pleys']",
        "RPLS"
    ],
    "replaced": [
        "[ri,pleys,d]",
        "RPLST"
    ],
    "replacement": [
        "[ri,pleys,muhnt]",
        "RPLSMNT"
    ],
    "replacements": [
        "['ri', 'pleys', 'muhnt', 's']",
        "RPLSMNTS"
    ],
    "replay": [
        "[verbree,pley]",
        "RPL"
    ],
    "reply": [
        "['ri', 'plahy']",
        "RPL"
    ],
    "report": [
        "['ri', 'pawrt']",
        "RPRT"
    ],
    "reporting": [
        "[ri,pawrt,ing]",
        "RPRTNK"
    ],
    "represent": [
        "['rep', 'ri', 'zent']",
        "RPRSNT"
    ],
    "reps": [
        "[rep,s]",
        "RPS"
    ],
    "reptile": [
        "[rep,til]",
        "RPTL"
    ],
    "republic": [
        "[ri,puhb,lik]",
        "RPPLK"
    ],
    "republican": [
        "[ri,puhb,li,kuhn]",
        "RPPLKN"
    ],
    "reputation": [
        "['rep', 'yuh', 'tey', 'shuhn']",
        "RPTXN"
    ],
    "request": [
        "['ri', 'kwest']",
        "RKST"
    ],
    "require": [
        "['ri', 'kwahyuhr']",
        "RKR"
    ],
    "required": [
        "[ri,kwahyuhr,d]",
        "RKRT"
    ],
    "reruns": [
        "[verbree,ruhn,s]",
        "RRNS"
    ],
    "rescue": [
        "['res', 'kyoo']",
        "RSK"
    ],
    "research": [
        "['ri', 'surch']",
        "RSRX"
    ],
    "resemble": [
        "['ri', 'zem', 'buhl']",
        "RSMPL"
    ],
    "reservations": [
        "[rez,er,vey,shuhn,s]",
        "RSRFXNS"
    ],
    "reserve": [
        "['ri', 'zurv']",
        "RSRF"
    ],
    "reserved": [
        "[ri,zurvd]",
        "RSRFT"
    ],
    "reset": [
        "['verbree', 'set']",
        "RST"
    ],
    "reside": [
        "['ri', 'zahyd']",
        "RST"
    ],
    "residence": [
        "['rez', 'i', 'duhns']",
        "RSTNS"
    ],
    "resident": [
        "['rez', 'i', 'duhnt']",
        "RSTNT"
    ],
    "residential": [
        "[rez,i,den,shuhl]",
        "RSTNXL"
    ],
    "residue": [
        "['rez', 'i', 'doo']",
        "RST"
    ],
    "resist": [
        "[ri,zist]",
        "RSST"
    ],
    "resolution": [
        "[rez,uh,loo,shuhn]",
        "RSLXN"
    ],
    "resort": [
        "['ri', 'zawrt']",
        "RSRT"
    ],
    "respect": [
        "['ri', 'spekt']",
        "RSPKT"
    ],
    "respected": [
        "['ri', 'spekt', 'ed']",
        "RSPKTT"
    ],
    "respectful": [
        "[ri,spekt,fuhl]",
        "RSPKTFL"
    ],
    "respecting": [
        "[ri,spek,ting]",
        "RSPKTNK"
    ],
    "respond": [
        "['ri', 'spond']",
        "RSPNT"
    ],
    "response": [
        "['ri', 'spons']",
        "RSPNS"
    ],
    "responsibility": [
        "[ri,spon,suh,bil,i,tee]",
        "RSPNSPLT"
    ],
    "responsible": [
        "['ri', 'spon', 'suh', 'buhl']",
        "RSPNSPL"
    ],
    "rest": [
        "['rest']",
        "RST"
    ],
    "restaurant": [
        "['res', 'ter', 'uhnt']",
        "RSTRNT"
    ],
    "restaurants": [
        "[res,ter,uhnt,s]",
        "RSTRNTS"
    ],
    "resting": [
        "['res', 'ting']",
        "RSTNK"
    ],
    "restless": [
        "[rest,lis]",
        "RSTLS"
    ],
    "restore": [
        "['ri', 'stawr']",
        "RSTR"
    ],
    "restored": [
        "[ri,stawr,d]",
        "RSTRT"
    ],
    "result": [
        "[ri,zuhlt]",
        "RSLT"
    ],
    "results": [
        "[ri,zuhlt,s]",
        "RSLTS"
    ],
    "resume": [
        "[ri,zoom]",
        "RSM"
    ],
    "resurrect": [
        "[rez,uh,rekt]",
        "RSRKT"
    ],
    "retail": [
        "['ree', 'teylfor14']",
        "RTL"
    ],
    "retard": [
        "[ri,tahrd]",
        "RTRT"
    ],
    "retarded": [
        "['ri', 'tahr', 'did']",
        "RTRTT"
    ],
    "retards": [
        "['ri', 'tahrd', 's']",
        "RTRTS"
    ],
    "rethink": [
        "[verbree,thingk]",
        "R0NK"
    ],
    "retire": [
        "['ri', 'tahyuhr']",
        "RTR"
    ],
    "retired": [
        "[ri,tahyuhrd]",
        "RTRT"
    ],
    "retirement": [
        "['ri', 'tahyuhr', 'muhnt']",
        "RTRMNT"
    ],
    "retiring": [
        "[ri,tahyuhr,ing]",
        "RTRNK"
    ],
    "retract": [
        "[ri,trakt]",
        "RTRKT"
    ],
    "retreat": [
        "['ri', 'treet']",
        "RTRT"
    ],
    "retro": [
        "['re', 'troh']",
        "RTR"
    ],
    "return": [
        "['ri', 'turn']",
        "RTRN"
    ],
    "reunion": [
        "[ree,yoon,yuhn]",
        "RNN"
    ],
    "reunite": [
        "[ree,yoo,nahyt]",
        "RNT"
    ],
    "reveal": [
        "[ri,veel]",
        "RFL"
    ],
    "revelations": [
        "[rev,uh,ley,shuhn,s]",
        "RFLXNS"
    ],
    "revenge": [
        "[ri,venj]",
        "RFNJ"
    ],
    "revenue": [
        "['rev', 'uhn', 'yoo']",
        "RFN"
    ],
    "reverend": [
        "['rev', 'er', 'uhnd']",
        "RFRNT"
    ],
    "reverse": [
        "['ri', 'vurs']",
        "RFRS"
    ],
    "review": [
        "[ri,vyoo]",
        "RF"
    ],
    "revisit": [
        "[re-,viz,it]",
        "RFST"
    ],
    "revival": [
        "[ri,vahy,vuhl]",
        "RFFL"
    ],
    "revive": [
        "[ri,vahyv]",
        "RFF"
    ],
    "revolution": [
        "['rev', 'uh', 'loo', 'shuhn']",
        "RFLXN"
    ],
    "revolutionary": [
        "['rev', 'uh', 'loo', 'shuh', 'ner', 'ee']",
        "RFLXNR"
    ],
    "revolver": [
        "[ri,vol,ver]",
        "RFLFR"
    ],
    "revolving": [
        "['ri', 'vol', 'ving']",
        "RFLFNK"
    ],
    "reward": [
        "[ri,wawrd]",
        "RRT"
    ],
    "rewarded": [
        "[ri,wawrd,ed]",
        "RRTT"
    ],
    "rewind": [
        "['verbree', 'wahynd']",
        "RNT"
    ],
    "rewinding": [
        "[verbree,wahynd,ing]",
        "RNTNK"
    ],
    "rewrite": [
        "[verbree,rahyt]",
        "RRT"
    ],
    "rex": [
        "['reks']",
        "RKS"
    ],
    "rhetoric": [
        "[ret,er,ik]",
        "RTRK"
    ],
    "rhine": [
        "[rahyn]",
        "RN"
    ],
    "rhinestone": [
        "[rahyn,stohn]",
        "RNSTN"
    ],
    "rhino": [
        "['rahy', 'noh']",
        "RN"
    ],
    "rhyme": [
        "['rahym']",
        "RM"
    ],
    "rhymed": [
        "[rahym,d]",
        "RMT"
    ],
    "rhymer": [
        "[rahym,r]",
        "RMR"
    ],
    "rhymes": [
        "['rahym', 's']",
        "RMS"
    ],
    "rhythm": [
        "['rith', 'uhm']",
        "R0M"
    ],
    "rib": [
        "['rib']",
        "RP"
    ],
    "ribbon": [
        "[rib,uhn]",
        "RPN"
    ],
    "ribbons": [
        "[rib,uhn,s]",
        "RPNS"
    ],
    "ribs": [
        "['rib', 's']",
        "RPS"
    ],
    "ricardo": [
        "['ri', 'kahr', 'doh']",
        "RKRT"
    ],
    "rice": [
        "['rahys']",
        "RS"
    ],
    "rich": [
        "['rich']",
        "RX"
    ],
    "richer": [
        "['rich', 'er']",
        "RXR"
    ],
    "riches": [
        "['rich', 'iz']",
        "RXS"
    ],
    "richest": [
        "['rich', 'est']",
        "RXST"
    ],
    "richmond": [
        "[rich,muhnd]",
        "RXMNT"
    ],
    "richter": [
        "['rik', 'ter']",
        "RKTR"
    ],
    "rick": [
        "['rik']",
        "RK"
    ],
    "ricky": [
        "['rik', 'ee']",
        "RK"
    ],
    "rico": [
        "['ree', 'koh']",
        "RK"
    ],
    "rid": [
        "['rid']",
        "RT"
    ],
    "riddance": [
        "[rid,ns]",
        "RTNS"
    ],
    "riddle": [
        "['rid', 'l']",
        "RTL"
    ],
    "ride": [
        "['rahyd']",
        "RT"
    ],
    "ride's": [
        "[rahyd,'s]",
        "RTS"
    ],
    "rider": [
        "['rahy', 'der']",
        "RTR"
    ],
    "riders": [
        "['rahy', 'der', 's']",
        "RTRS"
    ],
    "rides": [
        "['rahyd', 's']",
        "RTS"
    ],
    "ridge": [
        "['rij']",
        "RJ"
    ],
    "ridicule": [
        "['rid', 'i', 'kyool']",
        "RTKL"
    ],
    "ridiculous": [
        "['ri', 'dik', 'yuh', 'luhs']",
        "RTKLS"
    ],
    "riding": [
        "['rahy', 'ding']",
        "RTNK"
    ],
    "riesling": [
        "[reez,ling]",
        "RSLNK"
    ],
    "riff": [
        "[rif]",
        "RF"
    ],
    "rifle": [
        "['rahy', 'fuhl']",
        "RFL"
    ],
    "rifles": [
        "['rahy', 'fuhl', 's']",
        "RFLS"
    ],
    "right": [
        "['rahyt']",
        "RT"
    ],
    "righteous": [
        "['rahy', 'chuhs']",
        "RTS"
    ],
    "rights": [
        "['rahyts']",
        "RTS"
    ],
    "rigor": [
        "[rig,er]",
        "RKR"
    ],
    "riley": [
        "['rahy', 'lee']",
        "RL"
    ],
    "rim": [
        "['rim']",
        "RM"
    ],
    "rims": [
        "['rim', 's']",
        "RMS"
    ],
    "rinds": [
        "['rahynd', 's']",
        "RNTS"
    ],
    "ring": [
        "['ring']",
        "RNK"
    ],
    "ringer": [
        "['ring', 'er']",
        "RNKR"
    ],
    "ringing": [
        "['ring', 'ing']",
        "RNJNK"
    ],
    "ringleader": [
        "[ring,lee,der]",
        "RNKLTR"
    ],
    "rings": [
        "['ring', 's']",
        "RNKS"
    ],
    "rink": [
        "[ringk]",
        "RNK"
    ],
    "rinse": [
        "['rins']",
        "RNS"
    ],
    "rio": [
        "['ree', 'ohdeyzhuh', 'nair', 'oh', '']",
        "R"
    ],
    "riot": [
        "['rahy', 'uht']",
        "RT"
    ],
    "riots": [
        "[rahy,uht,s]",
        "RTS"
    ],
    "rip": [
        "['rip']",
        "RP"
    ],
    "ripe": [
        "['rahyp']",
        "RP"
    ],
    "ripped": [
        "['ript']",
        "RPT"
    ],
    "ripper": [
        "[rip,er]",
        "RPR"
    ],
    "ripping": [
        "['rip', 'ing']",
        "RPNK"
    ],
    "rise": [
        "['rahyz']",
        "RS"
    ],
    "rising": [
        "[rahy,zing]",
        "RSNK"
    ],
    "risk": [
        "['risk']",
        "RSK"
    ],
    "risked": [
        "['risk', 'ed']",
        "RSKT"
    ],
    "risking": [
        "['risk', 'ing']",
        "RSKNK"
    ],
    "risks": [
        "['risk', 's']",
        "RSKS"
    ],
    "risky": [
        "[ris,kee]",
        "RSK"
    ],
    "ritalin": [
        "['rit', 'l', 'in']",
        "RTLN"
    ],
    "rite": [
        "[rahyt]",
        "RT"
    ],
    "ritual": [
        "['rich', 'oo', 'uhl']",
        "RTL"
    ],
    "ritz": [
        "['rits']",
        "RTS"
    ],
    "rival": [
        "[rahy,vuhl]",
        "RFL"
    ],
    "rivalry": [
        "[rahy,vuhl,ree]",
        "RFLR"
    ],
    "rivals": [
        "['rahy', 'vuhl', 's']",
        "RFLS"
    ],
    "river": [
        "['riv', 'er']",
        "RFR"
    ],
    "riverdale": [
        "['riv', 'er', 'deyl']",
        "RFRTL"
    ],
    "rivers": [
        "[riv,erz]",
        "RFRS"
    ],
    "riverside": [
        "[riv,er,sahyd]",
        "RFRST"
    ],
    "roach": [
        "[rohch]",
        "RX"
    ],
    "roaches": [
        "['rohch', 'es']",
        "RXS"
    ],
    "road": [
        "['rohd']",
        "RT"
    ],
    "roads": [
        "['rohd', 's']",
        "RTS"
    ],
    "roadster": [
        "['rohd', 'ster']",
        "RTSTR"
    ],
    "roam": [
        "[rohm]",
        "RM"
    ],
    "roaming": [
        "[rohm,ing]",
        "RMNK"
    ],
    "roar": [
        "[rawr]",
        "RR"
    ],
    "roaring": [
        "['rawr', 'ing']",
        "RRNK"
    ],
    "roars": [
        "[rawr,s]",
        "RRS"
    ],
    "roast": [
        "['rohst']",
        "RST"
    ],
    "roasted": [
        "['rohst', 'ed']",
        "RSTT"
    ],
    "roaster": [
        "[roh,ster]",
        "RSTR"
    ],
    "roasting": [
        "[roh,sting]",
        "RSTNK"
    ],
    "rob": [
        "['rob']",
        "RP"
    ],
    "robbed": [
        "['rob', 'bed']",
        "RPT"
    ],
    "robber": [
        "['rob', 'er']",
        "RPR"
    ],
    "robbers": [
        "['rob', 'er', 's']",
        "RPRS"
    ],
    "robbery": [
        "['rob', 'uh', 'ree']",
        "RPR"
    ],
    "robbing": [
        "['rob', 'bing']",
        "RPNK"
    ],
    "robe": [
        "['rohb']",
        "RP"
    ],
    "robert": [
        "['rob', 'ert']",
        "RPRT"
    ],
    "robes": [
        "[rohb,s]",
        "RPS"
    ],
    "robins": [
        "['rob', 'in', 's']",
        "RPNS"
    ],
    "robinson": [
        "[rob,in,suhn]",
        "RPNSN"
    ],
    "robot": [
        "['roh', 'buht']",
        "RPT"
    ],
    "robotic": [
        "['roh', 'buht', 'ic']",
        "RPTK"
    ],
    "robs": [
        "[rob,s]",
        "RPS"
    ],
    "roc": [
        "['rok']",
        "RK"
    ],
    "rock": [
        "['rok']",
        "RK"
    ],
    "rocked": [
        "['rok', 'ed']",
        "RKT"
    ],
    "rocker": [
        "[rok,er]",
        "RKR"
    ],
    "rocket": [
        "['rok', 'it']",
        "RKT"
    ],
    "rockets": [
        "[rok,it,s]",
        "RKTS"
    ],
    "rocking": [
        "['rok', 'ing']",
        "RKNK"
    ],
    "rocks": [
        "['rok', 's']",
        "RKS"
    ],
    "rockstar": [
        [
            "rok",
            "stahr"
        ],
        "RKSTR"
    ],
    "rocky": [
        "['rok', 'ee']",
        "RK"
    ],
    "rod": [
        "['rod']",
        "RT"
    ],
    "rode": [
        "['rohd']",
        "RT"
    ],
    "rodents": [
        "['rohd', 'nt', 's']",
        "RTNTS"
    ],
    "rodeo": [
        "['roh', 'dee', 'oh']",
        "RT"
    ],
    "rodman": [
        "['rod', 'muhn']",
        "RTMN"
    ],
    "rodney": [
        "['rod', 'nee']",
        "RTN"
    ],
    "roger": [
        "['roj', 'er']",
        "RKR"
    ],
    "rogers": [
        "[roj,erz]",
        "RKRS"
    ],
    "rogue": [
        "[rohg]",
        "RK"
    ],
    "role": [
        "['rohl']",
        "RL"
    ],
    "roles": [
        "[rohl,s]",
        "RLS"
    ],
    "rolex": [
        [
            "rohl",
            "eks"
        ],
        "RLKS"
    ],
    "roll": [
        "['rohl']",
        "RL"
    ],
    "roll's": [
        "[rohl,'s]",
        "RLL"
    ],
    "rolled": [
        "['rohl', 'ed']",
        "RLT"
    ],
    "roller": [
        "['roh', 'ler']",
        "RLR"
    ],
    "rollers": [
        "['roh', 'ler', 's']",
        "RLRS"
    ],
    "rollie": [
        [
            "rohl",
            "ee"
        ],
        "RL"
    ],
    "rolling": [
        "['roh', 'ling']",
        "RLNK"
    ],
    "rolls": [
        "['rohl', 's']",
        "RLS"
    ],
    "rom": [
        "[rohm]",
        "RM"
    ],
    "roman": [
        "['raw', 'mahn']",
        "RMN"
    ],
    "romance": [
        "['noun']",
        "RMNS"
    ],
    "romantic": [
        "['roh', 'man', 'tik']",
        "RMNTK"
    ],
    "rome": [
        "['rohm']",
        "RM"
    ],
    "romeo": [
        "[roh,mee,oh]",
        "RM"
    ],
    "ronald": [
        "['ron', 'ld']",
        "RNLT"
    ],
    "rondo": [
        "['ron', 'doh']",
        "RNT"
    ],
    "roof": [
        "['roof']",
        "RF"
    ],
    "rooftop": [
        "['roof', 'top']",
        "RFTP"
    ],
    "rookie": [
        "['rook', 'ee']",
        "RK"
    ],
    "rookies": [
        "['rook', 'ee', 's']",
        "RKS"
    ],
    "room": [
        "['room']",
        "RM"
    ],
    "roommate": [
        "[room,meyt]",
        "RMT"
    ],
    "rooms": [
        "['room', 's']",
        "RMS"
    ],
    "rooster": [
        "['roo', 'ster']",
        "RSTR"
    ],
    "root": [
        "['root']",
        "RT"
    ],
    "rooting": [
        "[root,ing]",
        "RTNK"
    ],
    "roots": [
        "['root', 's']",
        "RTS"
    ],
    "rope": [
        "['rohp']",
        "RP"
    ],
    "ropes": [
        "['rohp', 's']",
        "RPS"
    ],
    "rosa": [
        "['Italianraw', 'zah']",
        "RS"
    ],
    "roscoe": [
        "['ros', 'koh']",
        "RSK"
    ],
    "rose": [
        "['rohz']",
        "RS"
    ],
    "rosemary's": [
        "[rohz,mair,ee,'s]",
        "RSMRS"
    ],
    "roses": [
        "['rohz', 's']",
        "RSS"
    ],
    "ross": [
        "['raws']",
        "RS"
    ],
    "roster": [
        "['ros', 'ter']",
        "RSTR"
    ],
    "ros\u00e9": [
        "[roh,zey]",
        "RS"
    ],
    "ros\u00e9s": [
        "['roh', 'zey', 's']",
        "RSS"
    ],
    "rot": [
        "['rot']",
        "RT"
    ],
    "rotate": [
        "[roh,teytor]",
        "RTT"
    ],
    "rotation": [
        "['roh', 'tey', 'shuhn']",
        "RTXN"
    ],
    "rotten": [
        "['rot', 'n']",
        "RTN"
    ],
    "rottweiler": [
        "[rot,wahy,ler]",
        "RTLR"
    ],
    "rouge": [
        "[roozh]",
        "RJ"
    ],
    "rough": [
        "['ruhf']",
        "RF"
    ],
    "rougher": [
        "[ruhf,er]",
        "RFR"
    ],
    "roulette": [
        "['roo', 'let']",
        "RLT"
    ],
    "round": [
        "['round']",
        "RNT"
    ],
    "rounded": [
        "[roun,did]",
        "RNTT"
    ],
    "rounds": [
        "['round', 's']",
        "RNTS"
    ],
    "route": [
        "['root']",
        "RT"
    ],
    "routes": [
        "[root,s]",
        "RTS"
    ],
    "routine": [
        "['roo', 'teen']",
        "RTN"
    ],
    "rove": [
        "['rohv']",
        "RF"
    ],
    "rover": [
        "['roh', 'ver']",
        "RFR"
    ],
    "rovers": [
        "['roh', 'ver', 's']",
        "RFRS"
    ],
    "row": [
        "['roh']",
        "R"
    ],
    "rowdy": [
        "['rou', 'dee']",
        "RT"
    ],
    "rows": [
        "['roh', 's']",
        "RS"
    ],
    "royal": [
        "['roi', 'uhl']",
        "RL"
    ],
    "royalty": [
        "['roi', 'uhl', 'tee']",
        "RLT"
    ],
    "royce": [
        "['rois']",
        "RS"
    ],
    "rozay": [
        [
            "rohz",
            "ay"
        ],
        "RS"
    ],
    "ru": [
        "['r', 'thn', 'm']",
        "R"
    ],
    "rub": [
        "['ruhb']",
        "RP"
    ],
    "rubbed": [
        "[ruhb,bed]",
        "RPT"
    ],
    "rubber": [
        "['ruhb', 'er']",
        "RPR"
    ],
    "rubbers": [
        "[ruhb,er,s]",
        "RPRS"
    ],
    "rubbing": [
        "['ruhb', 'ing']",
        "RPNK"
    ],
    "rubbish": [
        "[ruhb,ish]",
        "RPX"
    ],
    "rubble": [
        "[ruhb,uhlorfor3]",
        "RPL"
    ],
    "rubs": [
        "[ruhb,s]",
        "RPS"
    ],
    "ruby": [
        "[roo,bee]",
        "RP"
    ],
    "ruck": [
        "[ruhk]",
        "RK"
    ],
    "ruckus": [
        "['ruhk', 'uhs']",
        "RKS"
    ],
    "rude": [
        "['rood']",
        "RT"
    ],
    "ruff": [
        "[ruhf]",
        "RF"
    ],
    "rug": [
        "['ruhg']",
        "RK"
    ],
    "ruga": [
        "[roo,guh]",
        "RK"
    ],
    "rugby": [
        "['ruhg', 'bee']",
        "RKP"
    ],
    "rugged": [
        "[ruhg,id]",
        "RKT"
    ],
    "rugs": [
        "['ruhg', 's']",
        "RKS"
    ],
    "ruined": [
        "['roo', 'in', 'ed']",
        "RNT"
    ],
    "rule": [
        "['rool']",
        "RL"
    ],
    "ruled": [
        "[rool,d]",
        "RLT"
    ],
    "ruler": [
        "['roo', 'ler']",
        "RLR"
    ],
    "rulers": [
        "['roo', 'ler', 's']",
        "RLRS"
    ],
    "rules": [
        "['rool', 's']",
        "RLS"
    ],
    "rum": [
        "['ruhm']",
        "RM"
    ],
    "rumble": [
        "['ruhm', 'buhl']",
        "RMPL"
    ],
    "rumbles": [
        "[ruhm,buhl,s]",
        "RMPLS"
    ],
    "rumor": [
        "['roo', 'mer']",
        "RMR"
    ],
    "rumors": [
        "['roo', 'mer', 's']",
        "RMRS"
    ],
    "rump": [
        "['ruhmp']",
        "RMP"
    ],
    "run": [
        "['ruhn']",
        "RN"
    ],
    "runaway": [
        "[ruhn,uh,wey]",
        "RN"
    ],
    "rung": [
        "[ruhng]",
        "RNK"
    ],
    "runner": [
        "['ruhn', 'er']",
        "RNR"
    ],
    "runners": [
        "[ruhn,er,s]",
        "RNRS"
    ],
    "running": [
        "['ruhn', 'ing']",
        "RNNK"
    ],
    "runny": [
        "[ruhn,ee]",
        "RN"
    ],
    "runs": [
        "['ruhn', 's']",
        "RNS"
    ],
    "runt": [
        "['ruhnt']",
        "RNT"
    ],
    "runway": [
        "['ruhn', 'wey']",
        "RN"
    ],
    "rush": [
        "['ruhsh']",
        "RX"
    ],
    "rushed": [
        "[ruhsh,ed]",
        "RXT"
    ],
    "rushing": [
        "['ruhsh', 'ing']",
        "RXNK"
    ],
    "russell": [
        "['ruhs', 'uhl']",
        "RSL"
    ],
    "russia": [
        "['ruhsh', 'uh']",
        "RS"
    ],
    "russian": [
        "['ruhsh', 'uhn']",
        "RSN"
    ],
    "russians": [
        "[ruhsh,uhn,s]",
        "RSNS"
    ],
    "rust": [
        "[ruhst]",
        "RST"
    ],
    "rusty": [
        "['ruhs', 'tee']",
        "RST"
    ],
    "ruth": [
        "['rooth']",
        "R0"
    ],
    "ruth's": [
        "['rooth', \"'s\"]",
        "R00"
    ],
    "ruthless": [
        "['rooth', 'lis']",
        "R0LS"
    ],
    "s": [
        "['es', '']",
        "S"
    ],
    "sa": [
        [
            "es",
            "ey"
        ],
        "S"
    ],
    "sabotage": [
        "['sab', 'uh', 'tahzh']",
        "SPTJ"
    ],
    "sabotages": [
        "[sab,uh,tahzh,s]",
        "SPTJS"
    ],
    "sac": [
        "['sak']",
        "SK"
    ],
    "sack": [
        "['sak']",
        "SK"
    ],
    "sacked": [
        "['sak', 'ed']",
        "SKT"
    ],
    "sacks": [
        "['sak', 's']",
        "SKS"
    ],
    "sacred": [
        "[sey,krid]",
        "SKRT"
    ],
    "sacrifice": [
        "['sak', 'ruh', 'fahys']",
        "SKRFS"
    ],
    "sacrificed": [
        "['sak', 'ruh', 'fahys', 'd']",
        "SKRFST"
    ],
    "sad": [
        "['sad']",
        "ST"
    ],
    "sadder": [
        "['sad', 'der']",
        "STR"
    ],
    "saddest": [
        "['sad', 'dest']",
        "STST"
    ],
    "saddle": [
        "[sad,l]",
        "STL"
    ],
    "sade": [
        "[sahd]",
        "ST"
    ],
    "sadly": [
        "[sad,ly]",
        "STL"
    ],
    "safari": [
        "['suh', 'fahr', 'ee']",
        "SFR"
    ],
    "safe": [
        "['seyf']",
        "SF"
    ],
    "safely": [
        "[seyf,ly]",
        "SFL"
    ],
    "safer": [
        "[seyf,r]",
        "SFR"
    ],
    "safest": [
        "[seyf,st]",
        "SFST"
    ],
    "safety": [
        "['seyf', 'tee']",
        "SFT"
    ],
    "sag": [
        "['sag']",
        "SK"
    ],
    "sagging": [
        "['sag', 'ging']",
        "SJNK"
    ],
    "said": [
        "['sed']",
        "ST"
    ],
    "sail": [
        "['seyl']",
        "SL"
    ],
    "sailing": [
        "[sey,ling]",
        "SLNK"
    ],
    "sailor": [
        "['sey', 'ler']",
        "SLR"
    ],
    "saint": [
        "['seynt']",
        "SNT"
    ],
    "saints": [
        "[seynt,s]",
        "SNTS"
    ],
    "sake": [
        "['seyk']",
        "SK"
    ],
    "sakes": [
        "[seyk,s]",
        "SKS"
    ],
    "saki": [
        "['sak', 'ee']",
        "SK"
    ],
    "salad": [
        "['sal', 'uhd']",
        "SLT"
    ],
    "salads": [
        "[sal,uhd,s]",
        "SLTS"
    ],
    "salary": [
        "['sal', 'uh', 'ree']",
        "SLR"
    ],
    "sale": [
        "['seyl']",
        "SL"
    ],
    "sales": [
        "[seylz]",
        "SLS"
    ],
    "saliva": [
        "[suh,lahy,vuh]",
        "SLF"
    ],
    "sally": [
        "['sal', 'ee']",
        "SL"
    ],
    "salmon": [
        "['sam', 'uhn']",
        "SLMN"
    ],
    "salon": [
        "['suh', 'lon']",
        "SLN"
    ],
    "salsa": [
        "['sahl', 'suh']",
        "SLS"
    ],
    "salt": [
        "['sawlt']",
        "SLT"
    ],
    "salty": [
        "['sawl', 'tee']",
        "SLT"
    ],
    "salute": [
        "['suh', 'loot']",
        "SLT"
    ],
    "sam": [
        "['sam']",
        "SM"
    ],
    "same": [
        "['seym']",
        "SM"
    ],
    "samoan": [
        "[suh,moh,uhn]",
        "SMN"
    ],
    "sample": [
        "['sam', 'puhl']",
        "SMPL"
    ],
    "sampled": [
        "[sam,puhl,d]",
        "SMPLT"
    ],
    "samples": [
        "[sam,puhl,s]",
        "SMPLS"
    ],
    "sams": [
        "['sam', 's']",
        "SMS"
    ],
    "samson": [
        "[sam,suhn]",
        "SMSN"
    ],
    "samuel": [
        "[sam,yoo,uhl]",
        "SML"
    ],
    "samurai": [
        "['sam', 'oo', 'rahy']",
        "SMR"
    ],
    "sand": [
        "['sand']",
        "SNT"
    ],
    "sandals": [
        "['san', 'dl', 's']",
        "SNTLS"
    ],
    "sanders": [
        "[san,der,s]",
        "SNTRS"
    ],
    "sands": [
        "[sand,s]",
        "SNTS"
    ],
    "sandwich": [
        "['sand', 'wich']",
        "SNTX"
    ],
    "sandwiches": [
        "['sand', 'wich', 'es']",
        "SNTXS"
    ],
    "sandy": [
        "['san', 'dee']",
        "SNT"
    ],
    "sane": [
        "['seyn']",
        "SN"
    ],
    "sang": [
        "['sang']",
        "SNK"
    ],
    "sanitize": [
        "['san', 'i', 'tahyz']",
        "SNTS"
    ],
    "sanitized": [
        "[san,i,tahyz,d]",
        "SNTST"
    ],
    "sanity": [
        "['san', 'i', 'tee']",
        "SNT"
    ],
    "sank": [
        "['sangk']",
        "SNK"
    ],
    "santa": [
        "['san', 'tuh']",
        "SNT"
    ],
    "santana": [
        "['san', 'tan', 'uh']",
        "SNTN"
    ],
    "sap": [
        "['sap']",
        "SP"
    ],
    "sarah": [
        "['sair', 'uh']",
        "SR"
    ],
    "saran": [
        "['suh', 'ran']",
        "SRN"
    ],
    "sarcastic": [
        "[sahr,kas,tik]",
        "SRKSTK"
    ],
    "sardines": [
        "['sahr', 'deen', 's']",
        "SRTNS"
    ],
    "sassy": [
        "[sas,ee]",
        "SS"
    ],
    "sat": [
        "['sat']",
        "ST"
    ],
    "satan": [
        "['seyt', 'n']",
        "STN"
    ],
    "satan's": [
        "[seyt,n,'s]",
        "STNNS"
    ],
    "satellite": [
        "['sat', 'l', 'ahyt']",
        "STLT"
    ],
    "satellites": [
        "[sat,l,ahyt,s]",
        "STLTS"
    ],
    "satisfaction": [
        "[sat,is,fak,shuhn]",
        "STSFKXN"
    ],
    "satisfied": [
        "['sat', 'is', 'fahyd']",
        "STSFT"
    ],
    "satisfy": [
        "['sat', 'is', 'fahy']",
        "STSF"
    ],
    "saturday": [
        "[sat,er,dey]",
        "STRT"
    ],
    "saturn": [
        "['sat', 'ern']",
        "STRN"
    ],
    "sauce": [
        "['saws']",
        "SS"
    ],
    "sauced": [
        "['sawst']",
        "SST"
    ],
    "saucing": [
        [
            "saws",
            "ing"
        ],
        "SSNK"
    ],
    "saucy": [
        "['saw', 'see']",
        "SS"
    ],
    "saudi": [
        "['sou', 'dee']",
        "ST"
    ],
    "sauna": [
        "['saw', 'nuh']",
        "SN"
    ],
    "sausage": [
        "[saw,sijor]",
        "SSJ"
    ],
    "savage": [
        "['sav', 'ij']",
        "SFJ"
    ],
    "savages": [
        "['sav', 'ij', 's']",
        "SFJS"
    ],
    "savannah": [
        "[suh,van,uh]",
        "SFN"
    ],
    "save": [
        "['seyv']",
        "SF"
    ],
    "saved": [
        "['seyv', 'd']",
        "SFT"
    ],
    "saver": [
        "[seyv,r]",
        "SFR"
    ],
    "savers": [
        "['seyv', 'rs']",
        "SFRS"
    ],
    "saving": [
        "['sey', 'ving']",
        "SFNK"
    ],
    "savings": [
        "[sey,ving,s]",
        "SFNKS"
    ],
    "savior": [
        "['seyv', 'yer']",
        "SFR"
    ],
    "savvy": [
        "[sav,ee]",
        "SF"
    ],
    "saw": [
        "['saw']",
        "S"
    ],
    "sawed": [
        "['saw', 'ed']",
        "ST"
    ],
    "sax": [
        "[saks]",
        "SKS"
    ],
    "say": [
        "['sey']",
        "S"
    ],
    "sayers": [
        "[sey,erz]",
        "SRS"
    ],
    "saying": [
        "['sey', 'ing']",
        "SNK"
    ],
    "sayonara": [
        "[sahy,uh,nahr,uh]",
        "SNR"
    ],
    "says": [
        "['sez']",
        "SS"
    ],
    "scab": [
        "[skab]",
        "SKP"
    ],
    "scale": [
        "['skeyl']",
        "SKL"
    ],
    "scales": [
        "[skeyl,s]",
        "SKLS"
    ],
    "scam": [
        "['skam']",
        "SKM"
    ],
    "scammers": [
        "[skam,mers]",
        "SKMRS"
    ],
    "scamming": [
        "[skam,ming]",
        "SKMNK"
    ],
    "scampi": [
        "['skam', 'pee']",
        "SKMP"
    ],
    "scams": [
        "[skam,s]",
        "SKMS"
    ],
    "scan": [
        "['skan']",
        "SKN"
    ],
    "scandal": [
        "['skan', 'dl']",
        "SKNTL"
    ],
    "scandalous": [
        "['skan', 'dl', 'uhs']",
        "SKNTLS"
    ],
    "scandals": [
        "[skan,dl,s]",
        "SKNTLS"
    ],
    "scanners": [
        "[skan,er,s]",
        "SKNRS"
    ],
    "scapegoat": [
        "[skeyp,goht]",
        "SKPKT"
    ],
    "scar": [
        "[skahr]",
        "SKR"
    ],
    "scare": [
        "['skair']",
        "SKR"
    ],
    "scarecrow": [
        "['skair', 'kroh']",
        "SKRKR"
    ],
    "scared": [
        "['skair', 'd']",
        "SKRT"
    ],
    "scarf": [
        "[skahrf]",
        "SKRF"
    ],
    "scarlet": [
        "[skahr,lit]",
        "SKRLT"
    ],
    "scarred": [
        "[skahr,red]",
        "SKRT"
    ],
    "scars": [
        "['skahr', 's']",
        "SKRS"
    ],
    "scary": [
        "['skair', 'ee']",
        "SKR"
    ],
    "scatter": [
        "[skat,er]",
        "SKTR"
    ],
    "scattered": [
        "[skat,erd]",
        "SKTRT"
    ],
    "scenario": [
        "[si,nair,ee,oh]",
        "SNR"
    ],
    "scene": [
        "['seen']",
        "SN"
    ],
    "scenery": [
        "[see,nuh,ree]",
        "SNR"
    ],
    "scenes": [
        "['seen', 's']",
        "SNS"
    ],
    "scenic": [
        "[see,nik]",
        "SNK"
    ],
    "scent": [
        "['sent']",
        "SNT"
    ],
    "scented": [
        "[sent,ed]",
        "SNTT"
    ],
    "schedule": [
        "['skej', 'ool']",
        "SKTL"
    ],
    "scheduled": [
        "[skej,ool,d]",
        "SKTLT"
    ],
    "scheme": [
        "['skeem']",
        "SKM"
    ],
    "schemes": [
        "[skeem,s]",
        "SKMS"
    ],
    "scheming": [
        "['skee', 'ming']",
        "SKMNK"
    ],
    "schizophrenic": [
        "['skit', 'suh', 'fren', 'ik']",
        "XSFRNK"
    ],
    "scholar": [
        "['skol', 'er']",
        "XLR"
    ],
    "scholars": [
        "[skol,er,s]",
        "XLRS"
    ],
    "scholarship": [
        "[skol,er,ship]",
        "XLRXP"
    ],
    "school": [
        "['skool']",
        "SKL"
    ],
    "school's": [
        "[skool,'s]",
        "SKLLS"
    ],
    "schoolboy": [
        "[skool,boi]",
        "SKLP"
    ],
    "schooled": [
        "[skool,ed]",
        "SKLT"
    ],
    "schooling": [
        "['skoo', 'ling']",
        "SKLNK"
    ],
    "schools": [
        "[skool,s]",
        "SKLS"
    ],
    "science": [
        "['sahy', 'uhns']",
        "SNS"
    ],
    "scientist": [
        "[sahy,uhn,tist]",
        "SNTST"
    ],
    "scientists": [
        "[sahy,uhn,tist,s]",
        "SNTSTS"
    ],
    "scissors": [
        "['siz', 'erz']",
        "SSRS"
    ],
    "scoob": [
        [
            "skoob"
        ],
        "SKP"
    ],
    "scoop": [
        "['skoop']",
        "SKP"
    ],
    "scooped": [
        "[skoop,ed]",
        "SKPT"
    ],
    "scooping": [
        "[skoop,ing]",
        "SKPNK"
    ],
    "scoot": [
        "['skoot']",
        "SKT"
    ],
    "scooter": [
        "['skoo', 'ter']",
        "SKTR"
    ],
    "scope": [
        "['skohp']",
        "SKP"
    ],
    "scorching": [
        "['skawr', 'ching']",
        "SKRXNK"
    ],
    "score": [
        "['skawr']",
        "SKR"
    ],
    "scoreboard": [
        "[skawr,bawrd]",
        "SKRPRT"
    ],
    "scored": [
        "['skawr', 'd']",
        "SKRT"
    ],
    "scores": [
        "['skawr', 's']",
        "SKRS"
    ],
    "scorpio": [
        "[skawr,pee,oh]",
        "SKRP"
    ],
    "scorsese": [
        "[skawr,sey,zee]",
        "SKRSS"
    ],
    "scotch": [
        "['skoch']",
        "SKX"
    ],
    "scott": [
        "['skot']",
        "SKT"
    ],
    "scottie": [
        "['skot', 'ee']",
        "SKT"
    ],
    "scotty": [
        "['skot', 'ee']",
        "SKT"
    ],
    "scout": [
        "[skout]",
        "SKT"
    ],
    "scram": [
        "['skram']",
        "SKM"
    ],
    "scramble": [
        "[skram,buhl]",
        "SKMPL"
    ],
    "scrambled": [
        "['skram', 'buhl', 'd']",
        "SKMPLT"
    ],
    "scrap": [
        "['skrap']",
        "SKP"
    ],
    "scrape": [
        "['skreyp']",
        "SKP"
    ],
    "scraper": [
        "[skrey,per]",
        "SKPR"
    ],
    "scraping": [
        "['skrey', 'ping']",
        "SKPNK"
    ],
    "scrapped": [
        "['skrap', 'ped']",
        "SKPT"
    ],
    "scrapping": [
        "['skrap', 'ping']",
        "SKPNK"
    ],
    "scrappy": [
        "[skrap,ee]",
        "SKP"
    ],
    "scraps": [
        "['skrap', 's']",
        "SKPS"
    ],
    "scratch": [
        "['skrach']",
        "SKX"
    ],
    "scratched": [
        "[skrach,ed]",
        "SKXT"
    ],
    "scratches": [
        "[skrach,iz]",
        "SKXS"
    ],
    "scratching": [
        "['skrach', 'ing']",
        "SKXNK"
    ],
    "scream": [
        "['skreem']",
        "SKM"
    ],
    "screamed": [
        "[skreem,ed]",
        "SKMT"
    ],
    "screaming": [
        "['skree', 'ming']",
        "SKMNK"
    ],
    "screams": [
        "['skreem', 's']",
        "SKMS"
    ],
    "screech": [
        "[skreech]",
        "SKX"
    ],
    "screen": [
        "['skreen']",
        "SKN"
    ],
    "screens": [
        "['skreen', 's']",
        "SKNS"
    ],
    "screw": [
        "['skroo']",
        "SK"
    ],
    "screwdriver": [
        "[skroo,drahy,ver]",
        "SKTRFR"
    ],
    "screwed": [
        "['skrood']",
        "SKT"
    ],
    "screwing": [
        "[skroo,ing]",
        "SKNK"
    ],
    "screws": [
        "['skroo', 's']",
        "SKS"
    ],
    "scrimmage": [
        "[skrim,ij]",
        "SKMJ"
    ],
    "script": [
        "['skript']",
        "SKPT"
    ],
    "scripted": [
        "[skript,ed]",
        "SKPTT"
    ],
    "scripture": [
        "[skrip,cher]",
        "SKPTR"
    ],
    "scriptures": [
        "[skrip,cher,s]",
        "SKPTRS"
    ],
    "scroll": [
        "['skrohl']",
        "SKL"
    ],
    "scrolling": [
        "['skrohl', 'ing']",
        "SKLNK"
    ],
    "scrooge": [
        "[skrooj]",
        "SKJ"
    ],
    "scrotum": [
        "[skroh,tuhm]",
        "SKTM"
    ],
    "scrub": [
        "['skruhb']",
        "SKP"
    ],
    "scrubs": [
        "[skruhb,s]",
        "SKPS"
    ],
    "scrutinize": [
        "[skroot,n,ahyz]",
        "SKTNS"
    ],
    "scuba": [
        "['skoo', 'buh']",
        "SKP"
    ],
    "scud": [
        "['skuhd']",
        "SKT"
    ],
    "scuff": [
        "['skuhf']",
        "SKF"
    ],
    "scummy": [
        "[skuhm,ee]",
        "SKM"
    ],
    "se": [
        "['s', 'ln', 'm']",
        "S"
    ],
    "sea": [
        "['see']",
        "S"
    ],
    "seafood": [
        "['see', 'food']",
        "SFT"
    ],
    "seal": [
        "['seel']",
        "SL"
    ],
    "sealed": [
        "['seel', 'ed']",
        "SLT"
    ],
    "seals": [
        "['seel', 's']",
        "SLS"
    ],
    "seam": [
        "['seem']",
        "SM"
    ],
    "seams": [
        "[seem,s]",
        "SMS"
    ],
    "seamstress": [
        "['seem', 'strisor']",
        "SMSTRS"
    ],
    "search": [
        "['surch']",
        "SRX"
    ],
    "searched": [
        "[surch,ed]",
        "SRXT"
    ],
    "searching": [
        "['sur', 'ching']",
        "SRXNK"
    ],
    "seas": [
        "['see', 's']",
        "SS"
    ],
    "seashells": [
        "['see', 'shel', 's']",
        "SXLS"
    ],
    "seashore": [
        "[see,shawr]",
        "SXR"
    ],
    "seasick": [
        "[see,sik]",
        "SSK"
    ],
    "season": [
        "['see', 'zuhn']",
        "SSN"
    ],
    "seasoned": [
        "[see,zuhn,ed]",
        "SSNT"
    ],
    "seasons": [
        "['see', 'zuhn', 's']",
        "SSNS"
    ],
    "seat": [
        "['seet']",
        "ST"
    ],
    "seated": [
        "['seet', 'ed']",
        "STT"
    ],
    "seater": [
        "['see', 'ter']",
        "STR"
    ],
    "seats": [
        "['seet', 's']",
        "STS"
    ],
    "seattle": [
        "['see', 'at', 'l']",
        "STL"
    ],
    "seaweed": [
        "['see', 'weed']",
        "ST"
    ],
    "sec": [
        "[sek]",
        "SK"
    ],
    "second": [
        "['sek', 'uhnd']",
        "SKNT"
    ],
    "seconds": [
        "['sek', 'uhnd', 's']",
        "SKNTS"
    ],
    "secret": [
        "['see', 'krit']",
        "SKRT"
    ],
    "secretary": [
        "['sek', 'ri', 'ter', 'ee']",
        "SKRTR"
    ],
    "secrets": [
        "['see', 'krit', 's']",
        "SKRTS"
    ],
    "section": [
        "['sek', 'shuhn']",
        "SKXN"
    ],
    "secure": [
        "['si', 'kyoor']",
        "SKR"
    ],
    "security": [
        "['si', 'kyoor', 'i', 'tee']",
        "SKRT"
    ],
    "sedan": [
        "[si,dan]",
        "STN"
    ],
    "sedated": [
        "['si', 'deyt', 'd']",
        "STTT"
    ],
    "seduce": [
        "[si,doos]",
        "STS"
    ],
    "seduction": [
        "[si,duhk,shuhn]",
        "STKXN"
    ],
    "see": [
        "['see']",
        "S"
    ],
    "see's": [
        "[see,'s]",
        "SS"
    ],
    "seed": [
        "['seed']",
        "ST"
    ],
    "seeds": [
        "['seed', 's']",
        "STS"
    ],
    "seeing": [
        "['see', 'ing']",
        "SNK"
    ],
    "seek": [
        "['seek']",
        "SK"
    ],
    "seeking": [
        "[seek,ing]",
        "SKNK"
    ],
    "seem": [
        "['seem']",
        "SM"
    ],
    "seemed": [
        "['seem', 'ed']",
        "SMT"
    ],
    "seeming": [
        "['see', 'ming']",
        "SMNK"
    ],
    "seems": [
        "['seem', 's']",
        "SMS"
    ],
    "seen": [
        "['seen']",
        "SN"
    ],
    "seersuckers": [
        "[seer,suhk,er,s]",
        "SRSKRS"
    ],
    "sees": [
        "['see', 's']",
        "SS"
    ],
    "segregated": [
        "[seg,ri,gey,tid]",
        "SKRKTT"
    ],
    "segregation": [
        "['seg', 'ri', 'gey', 'shuhn']",
        "SKRKXN"
    ],
    "seize": [
        "['seez']",
        "SS"
    ],
    "seized": [
        "['seez', 'd']",
        "SST"
    ],
    "seizure": [
        "['see', 'zher']",
        "SSR"
    ],
    "seizures": [
        "[see,zher,s]",
        "SSRS"
    ],
    "seldom": [
        "['sel', 'duhm']",
        "SLTM"
    ],
    "selection": [
        "[si,lek,shuhn]",
        "SLKXN"
    ],
    "self": [
        "['self']",
        "SLF"
    ],
    "selfish": [
        "['sel', 'fish']",
        "SLFX"
    ],
    "sell": [
        "['sel']",
        "SL"
    ],
    "seller": [
        "['sel', 'er']",
        "SLR"
    ],
    "selling": [
        "['sel', 'ing']",
        "SLNK"
    ],
    "sells": [
        "['sel', 's']",
        "SLS"
    ],
    "semen": [
        "['see', 'muhn']",
        "SMN"
    ],
    "semester": [
        "[si,mes,ter]",
        "SMSTR"
    ],
    "semi": [
        "['sem', 'ee']",
        "SM"
    ],
    "semis": [
        "['sey', 'mis']",
        "SMS"
    ],
    "send": [
        "['send']",
        "SNT"
    ],
    "sending": [
        "['send', 'ing']",
        "SNTNK"
    ],
    "sends": [
        "[send,s]",
        "SNTS"
    ],
    "senior": [
        "['seen', 'yer']",
        "SNR"
    ],
    "sensation": [
        "['sen', 'sey', 'shuhn']",
        "SNSXN"
    ],
    "sense": [
        "['sens']",
        "SNS"
    ],
    "senseless": [
        "[sens,lis]",
        "SNSLS"
    ],
    "senses": [
        "['sens', 's']",
        "SNSS"
    ],
    "sensitive": [
        "['sen', 'si', 'tiv']",
        "SNSTF"
    ],
    "sensuous": [
        "[sen,shoo,uhs]",
        "SNSS"
    ],
    "sent": [
        "['sent']",
        "SNT"
    ],
    "sentence": [
        "['sen', 'tns']",
        "SNTNS"
    ],
    "sentenced": [
        "[sen,tns,d]",
        "SNTNST"
    ],
    "sentences": [
        "[sen,tns,s]",
        "SNTNSS"
    ],
    "sentimental": [
        "['sen', 'tuh', 'men', 'tl']",
        "SNTMNTL"
    ],
    "separate": [
        "['verbsep', 'uh', 'reyt']",
        "SPRT"
    ],
    "separated": [
        "[verbsep,uh,reyt,d]",
        "SPRTT"
    ],
    "september": [
        "[sep,tem,ber]",
        "SPTMPR"
    ],
    "sequel": [
        "['see', 'kwuhl']",
        "SKL"
    ],
    "serenade": [
        "['ser', 'uh', 'neyd']",
        "SRNT"
    ],
    "sergeant": [
        "['sahr', 'juhnt']",
        "SRJNT"
    ],
    "serial": [
        "['seer', 'ee', 'uhl']",
        "SRL"
    ],
    "serious": [
        "['seer', 'ee', 'uhs']",
        "SRS"
    ],
    "seriously": [
        "['seer', 'ee', 'uhs', 'lee']",
        "SRSL"
    ],
    "sermon": [
        "[sur,muhn]",
        "SRMN"
    ],
    "serpent": [
        "['sur', 'puhnt']",
        "SRPNT"
    ],
    "serve": [
        "['surv']",
        "SRF"
    ],
    "served": [
        "['surv', 'd']",
        "SRFT"
    ],
    "serves": [
        "[surv,s]",
        "SRFS"
    ],
    "service": [
        "['sur', 'vis']",
        "SRFS"
    ],
    "services": [
        "[sur,vis,s]",
        "SRFSS"
    ],
    "serving": [
        "['sur', 'ving']",
        "SRFNK"
    ],
    "sesame": [
        "['ses', 'uh', 'mee']",
        "SSM"
    ],
    "session": [
        "['sesh', 'uhn']",
        "SSN"
    ],
    "sessions": [
        "[sesh,uhnz]",
        "SSNS"
    ],
    "set": [
        "['set']",
        "ST"
    ],
    "seth": [
        "['seth']",
        "S0"
    ],
    "sets": [
        "['set', 's']",
        "STS"
    ],
    "setting": [
        "['set', 'ing']",
        "STNK"
    ],
    "settle": [
        "['set', 'l']",
        "STL"
    ],
    "settled": [
        "[set,l,d]",
        "STLT"
    ],
    "settlement": [
        "['set', 'l', 'muhnt']",
        "STLMNT"
    ],
    "settles": [
        "[set,l,s]",
        "STLS"
    ],
    "settling": [
        "[set,ling]",
        "STLNK"
    ],
    "setup": [
        "[set,uhp]",
        "STP"
    ],
    "seven": [
        "['sev', 'uhn']",
        "SFN"
    ],
    "seventeen": [
        "['sev', 'uhn', 'teen']",
        "SFNTN"
    ],
    "seventh": [
        "['sev', 'uhnth']",
        "SFN0"
    ],
    "seventy": [
        "['sev', 'uhn', 'tee']",
        "SFNT"
    ],
    "several": [
        "['sev', 'er', 'uhl']",
        "SFRL"
    ],
    "severe": [
        "['suh', 'veer']",
        "SFR"
    ],
    "severed": [
        "[sev,er,ed]",
        "SFRT"
    ],
    "seville": [
        "[suh,vil]",
        "SFL"
    ],
    "sew": [
        "['soh']",
        "S"
    ],
    "sewed": [
        "['soh', 'ed']",
        "ST"
    ],
    "sewer": [
        "['soo', 'er']",
        "SR"
    ],
    "sewers": [
        "['soo', 'er', 's']",
        "SRS"
    ],
    "sewing": [
        "[soh,ing]",
        "SNK"
    ],
    "sex": [
        "['seks']",
        "SKS"
    ],
    "sexing": [
        "['seks', 'ing']",
        "SKSNK"
    ],
    "sexual": [
        "[sek,shoo,uhlor]",
        "SKSL"
    ],
    "sexually": [
        "[sek,shoo,uhlor,ly]",
        "SKSL"
    ],
    "sexy": [
        "['sek', 'see']",
        "SKS"
    ],
    "sg": [
        "['s', 'brg', 'm']",
        "SK"
    ],
    "shackled": [
        "[shak,uhl,d]",
        "XKLT"
    ],
    "shackles": [
        "[shak,uhl,s]",
        "XKLS"
    ],
    "shade": [
        "['sheyd']",
        "XT"
    ],
    "shaded": [
        "['shey', 'did']",
        "XTT"
    ],
    "shades": [
        "['sheyd', 's']",
        "XTS"
    ],
    "shadow": [
        "['shad', 'oh']",
        "XT"
    ],
    "shadows": [
        "[shad,oh,s]",
        "XTS"
    ],
    "shady": [
        "['shey', 'dee']",
        "XT"
    ],
    "shaft": [
        "[shaft]",
        "XFT"
    ],
    "shaggy": [
        "[shag,ee]",
        "XK"
    ],
    "shake": [
        "['sheyk']",
        "XK"
    ],
    "shaken": [
        "[sheyk,n]",
        "XKN"
    ],
    "shaker": [
        "[shey,ker]",
        "XKR"
    ],
    "shakes": [
        "['sheyk', 's']",
        "XKS"
    ],
    "shakespeare": [
        "[sheyk,speer]",
        "XKSPR"
    ],
    "shaking": [
        "['shey', 'king']",
        "XKNK"
    ],
    "shallow": [
        "[shal,oh]",
        "XL"
    ],
    "shame": [
        "['sheym']",
        "XM"
    ],
    "shameless": [
        "['sheym', 'lis']",
        "XMLS"
    ],
    "shampoo": [
        "[sham,poo]",
        "XMP"
    ],
    "shank": [
        "['shangk']",
        "XNK"
    ],
    "shape": [
        "['sheyp']",
        "XP"
    ],
    "shaped": [
        "['sheypt']",
        "XPT"
    ],
    "shaq": [
        [
            "shak"
        ],
        "XK"
    ],
    "share": [
        "['shair']",
        "XR"
    ],
    "shared": [
        "['shair', 'd']",
        "XRT"
    ],
    "shark": [
        "['shahrk']",
        "XRK"
    ],
    "sharks": [
        "['shahrk', 's']",
        "XRKS"
    ],
    "sharp": [
        "['shahrp']",
        "XRP"
    ],
    "sharpen": [
        "[shahr,puhn]",
        "XRPN"
    ],
    "sharpening": [
        "['shahr', 'puhn', 'ing']",
        "XRPNNK"
    ],
    "sharper": [
        "['shahr', 'per']",
        "XRPR"
    ],
    "shatter": [
        "[shat,er]",
        "XTR"
    ],
    "shattered": [
        "[shat,er,ed]",
        "XTRT"
    ],
    "shave": [
        "['sheyv']",
        "XF"
    ],
    "shaved": [
        "[sheyv,d]",
        "XFT"
    ],
    "shaving": [
        "[shey,ving]",
        "XFNK"
    ],
    "shaw": [
        "[shaw]",
        "X"
    ],
    "shawn": [
        "[shawn]",
        "XN"
    ],
    "shawty": [
        [
            "shaw",
            "tee"
        ],
        "XT"
    ],
    "she": [
        "['shee']",
        "X"
    ],
    "she'd": [
        "['sheed']",
        "XT"
    ],
    "she'll": [
        "['sheel']",
        "XL"
    ],
    "shed": [
        "['shed']",
        "XT"
    ],
    "shedding": [
        "[shed,ding]",
        "XTNK"
    ],
    "sheen": [
        "['sheen']",
        "XN"
    ],
    "sheep": [
        "['sheep']",
        "XP"
    ],
    "sheesh": [
        "['sheesh']",
        "XX"
    ],
    "sheet": [
        "['sheet']",
        "XT"
    ],
    "sheets": [
        "['sheet', 's']",
        "XTS"
    ],
    "shelf": [
        "['shelf']",
        "XLF"
    ],
    "shell": [
        "['shel']",
        "XL"
    ],
    "shells": [
        "['shel', 's']",
        "XLS"
    ],
    "shelves": [
        "[shelvz]",
        "XLFS"
    ],
    "shepard": [
        "['shep', 'erd']",
        "XPRT"
    ],
    "sheriff": [
        "['sher', 'if']",
        "XRF"
    ],
    "sherman": [
        "['shur', 'muhn']",
        "XRMN"
    ],
    "shield": [
        "[sheeld]",
        "XLT"
    ],
    "shift": [
        "['shift']",
        "XFT"
    ],
    "shifting": [
        "[shift,ing]",
        "XFTNK"
    ],
    "shifts": [
        "['shift', 's']",
        "XFTS"
    ],
    "shimmy": [
        "[shim,ee]",
        "XM"
    ],
    "shin": [
        "['shin']",
        "XN"
    ],
    "shine": [
        "['shahyn']",
        "XN"
    ],
    "shined": [
        "[shahyn,d]",
        "XNT"
    ],
    "shines": [
        "[shahyn,s]",
        "XNS"
    ],
    "shining": [
        "['shahy', 'ning']",
        "XNNK"
    ],
    "shinning": [
        "[shin,ning]",
        "XNNK"
    ],
    "shiny": [
        "['shahy', 'nee']",
        "XN"
    ],
    "ship": [
        "['ship']",
        "XP"
    ],
    "shipment": [
        "['ship', 'muhnt']",
        "XPMNT"
    ],
    "shipped": [
        "[ship,ped]",
        "XPT"
    ],
    "shipping": [
        "['ship', 'ing']",
        "XPNK"
    ],
    "ships": [
        "[ship,s]",
        "XPS"
    ],
    "shirt": [
        "['shurt']",
        "XRT"
    ],
    "shirts": [
        "[shurt,s]",
        "XRTS"
    ],
    "shit": [
        "['shit']",
        "XT"
    ],
    "shit's": [
        "['shit', \"'s\"]",
        "XTTS"
    ],
    "shits": [
        "['shit', 's']",
        "XTS"
    ],
    "shitting": [
        "['shit', 'ting']",
        "XTNK"
    ],
    "shitty": [
        "['shit', 'ee']",
        "XT"
    ],
    "shiver": [
        "[shiv,er]",
        "XFR"
    ],
    "shivering": [
        "['shiv', 'er', 'ing']",
        "XFRNK"
    ],
    "shivers": [
        "[shiv,er,s]",
        "XFRS"
    ],
    "shock": [
        "['shok']",
        "XK"
    ],
    "shocked": [
        "[shok,ed]",
        "XKT"
    ],
    "shocking": [
        "['shok', 'ing']",
        "XKNK"
    ],
    "shoe": [
        "['shoo']",
        "X"
    ],
    "shoes": [
        "['shoo', 's']",
        "XS"
    ],
    "shoo": [
        "['shoo']",
        "X"
    ],
    "shook": [
        "['shook']",
        "XK"
    ],
    "shoot": [
        "['shoot']",
        "XT"
    ],
    "shooter": [
        "['shoo', 'ter']",
        "XTR"
    ],
    "shooters": [
        "['shoo', 'ter', 's']",
        "XTRS"
    ],
    "shooting": [
        "['shoot', 'ing']",
        "XTNK"
    ],
    "shootout": [
        "[shoot,out]",
        "XTT"
    ],
    "shootouts": [
        "['shoot', 'out', 's']",
        "XTTS"
    ],
    "shoots": [
        "[shoot,s]",
        "XTS"
    ],
    "shop": [
        "['shop']",
        "XP"
    ],
    "shopaholic": [
        "[shop,uh,haw,lik]",
        "XPHLK"
    ],
    "shopper": [
        "[shop,er]",
        "XPR"
    ],
    "shopping": [
        "['shop', 'ing']",
        "XPNK"
    ],
    "shops": [
        "['shop', 's']",
        "XPS"
    ],
    "shore": [
        "['shawr']",
        "XR"
    ],
    "shores": [
        "[shawr,s]",
        "XRS"
    ],
    "short": [
        "['shawrt']",
        "XRT"
    ],
    "shorter": [
        "['shawr', 'ter']",
        "XRTR"
    ],
    "shortly": [
        "[shawrt,lee]",
        "XRTL"
    ],
    "shorts": [
        "['shawrt', 's']",
        "XRTS"
    ],
    "shot": [
        "['shot']",
        "XT"
    ],
    "shotgun": [
        "['shot', 'guhn']",
        "XTKN"
    ],
    "shotguns": [
        "[shot,guhn,s]",
        "XTKNS"
    ],
    "shots": [
        "['shot', 's']",
        "XTS"
    ],
    "should": [
        "['shood']",
        "XLT"
    ],
    "should've": [
        [
            "shood",
            "ahv"
        ],
        "XLTTF"
    ],
    "shoulder": [
        "['shohl', 'der']",
        "XLTR"
    ],
    "shoulders": [
        "['shohl', 'der', 's']",
        "XLTRS"
    ],
    "shouldn't": [
        "['shood', 'nt']",
        "XLTNNT"
    ],
    "shout": [
        "['shout']",
        "XT"
    ],
    "shouting": [
        "['shout', 'ing']",
        "XTNK"
    ],
    "shouts": [
        "['shout', 's']",
        "XTS"
    ],
    "shove": [
        "['shuhv']",
        "XF"
    ],
    "shovel": [
        "['shuhv', 'uhl']",
        "XFL"
    ],
    "show": [
        "['shoh']",
        "X"
    ],
    "showboat": [
        "['shoh', 'boht']",
        "XPT"
    ],
    "shower": [
        "['shou', 'er']",
        "XR"
    ],
    "showers": [
        "['shou', 'er', 's']",
        "XRS"
    ],
    "showing": [
        "['shoh', 'ing']",
        "XNK"
    ],
    "shown": [
        "[shohn]",
        "XN"
    ],
    "shows": [
        "['shoh', 's']",
        "XS"
    ],
    "showtime": [
        "['shoh', 'tahym']",
        "XTM"
    ],
    "shrimp": [
        "['shrimp']",
        "XRMP"
    ],
    "shrimps": [
        "[shrimp,s]",
        "XRMPS"
    ],
    "shrink": [
        "[shringk]",
        "XRNK"
    ],
    "shrinking": [
        "['shringk', 'ing']",
        "XRNKNK"
    ],
    "shrugs": [
        "[shruhg,s]",
        "XRKS"
    ],
    "shuck": [
        "['shuhk']",
        "XK"
    ],
    "shucks": [
        "[shuhk,s]",
        "XKS"
    ],
    "shudder": [
        "['shuhd', 'er']",
        "XTR"
    ],
    "shut": [
        "['shuht']",
        "XT"
    ],
    "shutting": [
        "['shuht', 'ting']",
        "XTNK"
    ],
    "shuttle": [
        "['shuht', 'l']",
        "XTL"
    ],
    "shy": [
        "['shahy']",
        "X"
    ],
    "si": [
        "[see]",
        "S"
    ],
    "siamese": [
        "[sahy,uh,meez]",
        "SMS"
    ],
    "siblings": [
        "[sib,ling,s]",
        "SPLNKS"
    ],
    "sic": [
        "['sik']",
        "SK"
    ],
    "sicily": [
        "['sis', 'uh', 'lee']",
        "SSL"
    ],
    "sick": [
        "['sik']",
        "SK"
    ],
    "sickening": [
        "['sik', 'uh', 'ning']",
        "SKNNK"
    ],
    "sicker": [
        "['sik', 'er']",
        "SKR"
    ],
    "sickest": [
        "[sik,est]",
        "SKST"
    ],
    "sickle": [
        "['sik', 'uhl']",
        "SKL"
    ],
    "sickness": [
        "[sik,nis]",
        "SKNS"
    ],
    "side": [
        "['sahyd']",
        "ST"
    ],
    "sidekick": [
        "['sahyd', 'kik']",
        "STKK"
    ],
    "sideline": [
        "[sahyd,lahyn]",
        "STLN"
    ],
    "sidelines": [
        "[sahyd,lahyn,s]",
        "STLNS"
    ],
    "sides": [
        "['sahyd', 's']",
        "STS"
    ],
    "sidetracked": [
        "[sahyd,trak,ed]",
        "STTRKT"
    ],
    "sidewalk": [
        "[sahyd,wawk]",
        "STLK"
    ],
    "sideways": [
        "[sahyd,weyz]",
        "STS"
    ],
    "sierra": [
        "[see,er,uh]",
        "SR"
    ],
    "sighed": [
        "[sahy,ed]",
        "ST"
    ],
    "sight": [
        "['sahyt']",
        "ST"
    ],
    "sighting": [
        "[sahyt,ing]",
        "STNK"
    ],
    "sights": [
        "[sahyt,s]",
        "STS"
    ],
    "sign": [
        "['sahyn']",
        "SN"
    ],
    "signal": [
        "['sig', 'nl']",
        "SNL"
    ],
    "signals": [
        "[sig,nl,s]",
        "SNLS"
    ],
    "signature": [
        "[sig,nuh,cher]",
        "SNTR"
    ],
    "signed": [
        "['sahyn', 'ed']",
        "SNT"
    ],
    "significant": [
        "[sig,nif,i,kuhnt]",
        "SNFKNT"
    ],
    "signing": [
        "[sahyn,ing]",
        "SNNK"
    ],
    "signs": [
        "['sahyn', 's']",
        "SNS"
    ],
    "silence": [
        "['sahy', 'luhns']",
        "SLNS"
    ],
    "silencer": [
        "['sahy', 'luhn', 'ser']",
        "SLNSR"
    ],
    "silent": [
        "['sahy', 'luhnt']",
        "SLNT"
    ],
    "silhouette": [
        "['sil', 'oo', 'et']",
        "SLT"
    ],
    "silicone": [
        "[sil,i,kohn]",
        "SLKN"
    ],
    "silk": [
        "['silk']",
        "SLK"
    ],
    "silky": [
        "[sil,kee]",
        "SLK"
    ],
    "silly": [
        "['sil', 'ee']",
        "SL"
    ],
    "silver": [
        "['sil', 'ver']",
        "SLFR"
    ],
    "similar": [
        "[sim,uh,ler]",
        "SMLR"
    ],
    "simmer": [
        "[sim,er]",
        "SMR"
    ],
    "simon": [
        "['sahy', 'muhn']",
        "SMN"
    ],
    "simons": [
        "['sahy', 'muhn', 's']",
        "SMNS"
    ],
    "simple": [
        "['sim', 'puhl']",
        "SMPL"
    ],
    "simply": [
        "['sim', 'plee']",
        "SMPL"
    ],
    "simpson": [
        "[simp,suhn]",
        "SMPSN"
    ],
    "sinatra": [
        "['si', 'nah', 'truh']",
        "SNTR"
    ],
    "since": [
        "['sins']",
        "SNS"
    ],
    "sincere": [
        "[sin,seer]",
        "SNSR"
    ],
    "sincerely": [
        "[sin,seer,ly]",
        "SNSRL"
    ],
    "sincerity": [
        "[sin,ser,i,tee]",
        "SNSRT"
    ],
    "sing": [
        "['sing']",
        "SNK"
    ],
    "singapore": [
        "['sing', 'guh', 'pawr']",
        "SNKPR"
    ],
    "singer": [
        "['sing', 'er']",
        "SNKR"
    ],
    "singers": [
        "['sing', 'er', 's']",
        "SNKRS"
    ],
    "singing": [
        "['sing', 'ing']",
        "SNJNK"
    ],
    "single": [
        "['sing', 'guhl']",
        "SNKL"
    ],
    "singles": [
        "[sing,guhl,s]",
        "SNKLS"
    ],
    "sings": [
        "['sing', 's']",
        "SNKS"
    ],
    "sinister": [
        "[sin,uh,ster]",
        "SNSTR"
    ],
    "sink": [
        "['singk']",
        "SNK"
    ],
    "sinking": [
        "[singk,ing]",
        "SNKNK"
    ],
    "sinned": [
        "['sin', 'ned']",
        "SNT"
    ],
    "sinner": [
        "['sin', 'er']",
        "SNR"
    ],
    "sinners": [
        "['sin', 'er', 's']",
        "SNRS"
    ],
    "sinning": [
        "['sin', 'ning']",
        "SNNK"
    ],
    "sins": [
        "['sinz']",
        "SNS"
    ],
    "sinus": [
        "['sahy', 'nuhs']",
        "SNS"
    ],
    "sip": [
        "['sip']",
        "SP"
    ],
    "sipped": [
        "['sip', 'ped']",
        "SPT"
    ],
    "sipper": [
        "[sip,er]",
        "SPR"
    ],
    "sippers": [
        "[sip,er,s]",
        "SPRS"
    ],
    "sipping": [
        "['sip', 'ping']",
        "SPNK"
    ],
    "sips": [
        "[sip,s]",
        "SPS"
    ],
    "sir": [
        "['sur']",
        "SR"
    ],
    "sire": [
        "[sahyuhr]",
        "SR"
    ],
    "siren": [
        "['sahy', 'ruhn']",
        "SRN"
    ],
    "sirens": [
        "['sahy', 'ruhn', 's']",
        "SRNS"
    ],
    "sirloin": [
        "['sur', 'loin']",
        "SRLN"
    ],
    "sis": [
        "['sis']",
        "SS"
    ],
    "sissy": [
        "[sis,ee]",
        "SS"
    ],
    "sister": [
        "['sis', 'ter']",
        "SSTR"
    ],
    "sister's": [
        "['sis', 'ter', \"'s\"]",
        "SSTRRS"
    ],
    "sisters": [
        "['sis', 'ter', 's']",
        "SSTRS"
    ],
    "sit": [
        "['sit']",
        "ST"
    ],
    "site": [
        "['sahyt']",
        "ST"
    ],
    "sits": [
        "['sit', 's']",
        "STS"
    ],
    "sitter": [
        "[sit,er]",
        "STR"
    ],
    "sitting": [
        "['sit', 'ing']",
        "STNK"
    ],
    "situation": [
        "['sich', 'oo', 'ey', 'shuhn']",
        "STXN"
    ],
    "situations": [
        "['sich', 'oo', 'ey', 'shuhn', 's']",
        "STXNS"
    ],
    "six": [
        "['siks']",
        "SKS"
    ],
    "sixer": [
        "['siks', 'er']",
        "SKSR"
    ],
    "sixes": [
        "['siks', 'es']",
        "SKSS"
    ],
    "sixteen": [
        "['siks', 'teen']",
        "SKSTN"
    ],
    "sixth": [
        "['siksth']",
        "SKS0"
    ],
    "sixty": [
        "['siks', 'tee']",
        "SKST"
    ],
    "size": [
        "['sahyz']",
        "SS"
    ],
    "sized": [
        "[sahyzd]",
        "SST"
    ],
    "sizzle": [
        "[siz,uhl]",
        "SSL"
    ],
    "sizzling": [
        [
            "siz",
            "uhl",
            "ing"
        ],
        "SSLNK"
    ],
    "skate": [
        "['skeyt']",
        "SKT"
    ],
    "skateboard": [
        "[skeyt,bawrd]",
        "SKTPRT"
    ],
    "skated": [
        "[skeyt,d]",
        "SKTT"
    ],
    "skater": [
        "['skey', 'ter']",
        "SKTR"
    ],
    "skaters": [
        "[skey,ter,s]",
        "SKTRS"
    ],
    "skates": [
        "[skeyt,s]",
        "SKTS"
    ],
    "skeet": [
        "['skeet']",
        "SKT"
    ],
    "skeleton": [
        "['skel', 'i', 'tn']",
        "SKLTN"
    ],
    "skeletons": [
        "[skel,i,tn,s]",
        "SKLTNS"
    ],
    "skeptic": [
        "[skep,tik]",
        "SKPTK"
    ],
    "sketch": [
        "['skech']",
        "SKX"
    ],
    "sketchy": [
        "['skech', 'ee']",
        "SKX"
    ],
    "skewed": [
        "[skyoo,ed]",
        "SKT"
    ],
    "ski": [
        "['skee']",
        "SK"
    ],
    "skies": [
        "['skahyz']",
        "SKS"
    ],
    "skiing": [
        "['skee', 'ing']",
        "SKNK"
    ],
    "skill": [
        "[skil]",
        "SKL"
    ],
    "skilled": [
        "[skild]",
        "SKLT"
    ],
    "skillet": [
        "['skil', 'it']",
        "SKLT"
    ],
    "skills": [
        "['skil', 's']",
        "SKLS"
    ],
    "skin": [
        "['skin']",
        "SKN"
    ],
    "skinned": [
        "['skin', 'ned']",
        "SKNT"
    ],
    "skinnies": [
        [
            "skin",
            "ees"
        ],
        "SKNS"
    ],
    "skinny": [
        "['skin', 'ee']",
        "SKN"
    ],
    "skins": [
        "[skin,s]",
        "SKNS"
    ],
    "skip": [
        "['skip']",
        "SKP"
    ],
    "skipped": [
        "[skip,ped]",
        "SKPT"
    ],
    "skipper": [
        "[skip,er]",
        "SKPR"
    ],
    "skipping": [
        "['skip', 'ping']",
        "SKPNK"
    ],
    "skips": [
        "[skip,s]",
        "SKPS"
    ],
    "skirt": [
        "['skurt']",
        "SKRT"
    ],
    "skirts": [
        "['skurt', 's']",
        "SKRTS"
    ],
    "skis": [
        "['skee', 's']",
        "SKS"
    ],
    "skits": [
        "[skit,s]",
        "SKTS"
    ],
    "skittle": [
        "['skit', 'l']",
        "SKTL"
    ],
    "skittles": [
        "['skit', 'l', 's']",
        "SKTLS"
    ],
    "skull": [
        "['skuhl']",
        "SKL"
    ],
    "skunk": [
        "[skuhngk]",
        "SKNK"
    ],
    "sky": [
        "['skahy']",
        "SK"
    ],
    "sky's": [
        "['skahy', \"'s\"]",
        "SKS"
    ],
    "skydive": [
        "[skahy,dahyv]",
        "SKTF"
    ],
    "skyline": [
        "[skahy,lahyn]",
        "SKLN"
    ],
    "skype": [
        "['skahyp']",
        "SKP"
    ],
    "skyscrapers": [
        "['skahy', 'skrey', 'per', 's']",
        "SKSKPRS"
    ],
    "slab": [
        "[slab]",
        "SLP"
    ],
    "slabs": [
        "[slab,s]",
        "SLPS"
    ],
    "slack": [
        "[slak]",
        "SLK"
    ],
    "slackers": [
        "[slak,er,s]",
        "SLKRS"
    ],
    "slacking": [
        "[slak,ing]",
        "SLKNK"
    ],
    "slacks": [
        "[slaks]",
        "SLKS"
    ],
    "slain": [
        "['sleyn']",
        "SLN"
    ],
    "slalom": [
        "[slah,luhm]",
        "SLLM"
    ],
    "slam": [
        "['slam']",
        "SLM"
    ],
    "slammed": [
        "[slam,med]",
        "SLMT"
    ],
    "slammer": [
        "['slam', 'er']",
        "SLMR"
    ],
    "slamming": [
        "['slam', 'ing']",
        "SLMNK"
    ],
    "slang": [
        "['slang']",
        "SLNK"
    ],
    "slanging": [
        "['slang', 'ing']",
        "SLNJNK"
    ],
    "slant": [
        "[slant]",
        "SLNT"
    ],
    "slanted": [
        "[slant,ed]",
        "SLNTT"
    ],
    "slap": [
        "['slap']",
        "SLP"
    ],
    "slapped": [
        "['slap', 'ped']",
        "SLPT"
    ],
    "slapping": [
        "['slap', 'ping']",
        "SLPNK"
    ],
    "slaps": [
        "['slap', 's']",
        "SLPS"
    ],
    "slash": [
        "['slash']",
        "SLX"
    ],
    "slaughter": [
        "['slaw', 'ter']",
        "SLFTR"
    ],
    "slaughtered": [
        "[slaw,ter,ed]",
        "SLFTRT"
    ],
    "slaughterhouse": [
        "[slaw,ter,hous]",
        "SLFTRS"
    ],
    "slave": [
        "['sleyv']",
        "SLF"
    ],
    "slaved": [
        "['sleyv', 'd']",
        "SLFT"
    ],
    "slavery": [
        "['sley', 'vuh', 'ree']",
        "SLFR"
    ],
    "slaves": [
        "['sleyv', 's']",
        "SLFS"
    ],
    "slay": [
        "['sley']",
        "SL"
    ],
    "slayed": [
        "['sley', 'ed']",
        "SLT"
    ],
    "slaying": [
        "['sley', 'ing']",
        "SLNK"
    ],
    "sleazy": [
        "[slee,zee]",
        "SLS"
    ],
    "sled": [
        "['sled']",
        "SLT"
    ],
    "sledgehammer": [
        "['slej', 'ham', 'er']",
        "SLJHMR"
    ],
    "sleep": [
        "['sleep']",
        "SLP"
    ],
    "sleeper": [
        "[slee,per]",
        "SLPR"
    ],
    "sleeping": [
        "['slee', 'ping']",
        "SLPNK"
    ],
    "sleepless": [
        "['sleep', 'lis']",
        "SLPLS"
    ],
    "sleeps": [
        "[sleep,s]",
        "SLPS"
    ],
    "sleepy": [
        "['slee', 'pee']",
        "SLP"
    ],
    "sleet": [
        "[sleet]",
        "SLT"
    ],
    "sleeve": [
        "['sleev']",
        "SLF"
    ],
    "sleeved": [
        "['sleev', 'd']",
        "SLFT"
    ],
    "sleeveless": [
        "[sleev,lis]",
        "SLFLS"
    ],
    "sleeves": [
        "['sleev', 's']",
        "SLFS"
    ],
    "sleigh": [
        "['sley']",
        "SL"
    ],
    "slept": [
        "['slept']",
        "SLPT"
    ],
    "slew": [
        "[sloo]",
        "SL"
    ],
    "slice": [
        "['slahys']",
        "SLS"
    ],
    "slices": [
        "['slahys', 's']",
        "SLSS"
    ],
    "slick": [
        "['slik']",
        "SLK"
    ],
    "slicker": [
        "['slik', 'er']",
        "SLKR"
    ],
    "slickest": [
        "[slik,est]",
        "SLKST"
    ],
    "slid": [
        "['slahyd', '']",
        "SLT"
    ],
    "slide": [
        "['slahyd']",
        "SLT"
    ],
    "slides": [
        "[slahyd,s]",
        "SLTS"
    ],
    "sliding": [
        "['slahy', 'ding']",
        "SLTNK"
    ],
    "slight": [
        "['slahyt']",
        "SLT"
    ],
    "slightest": [
        "[slahyt,est]",
        "SLTST"
    ],
    "slightly": [
        "[slahyt,ly]",
        "SLTL"
    ],
    "slim": [
        "['slim']",
        "SLM"
    ],
    "slime": [
        "['slahym']",
        "SLM"
    ],
    "slimes": [
        "['slahym', 's']",
        "SLMS"
    ],
    "sling": [
        "[sling]",
        "SLNK"
    ],
    "slinging": [
        "['sling', 'ing']",
        "SLNJNK"
    ],
    "slip": [
        "['slip']",
        "SLP"
    ],
    "slipped": [
        "['slip', 'ped']",
        "SLPT"
    ],
    "slippers": [
        "['slip', 'er', 's']",
        "SLPRS"
    ],
    "slippery": [
        "['slip', 'uh', 'ree']",
        "SLPR"
    ],
    "slipping": [
        "['slip', 'ping']",
        "SLPNK"
    ],
    "slips": [
        "['slip', 's']",
        "SLPS"
    ],
    "slit": [
        "['slit']",
        "SLT"
    ],
    "slither": [
        "[slith,er]",
        "SL0R"
    ],
    "slob": [
        "['slob']",
        "SLP"
    ],
    "slop": [
        "['slop']",
        "SLP"
    ],
    "slope": [
        "[slohp]",
        "SLP"
    ],
    "sloppy": [
        "['slop', 'ee']",
        "SLP"
    ],
    "slot": [
        "[slot]",
        "SLT"
    ],
    "slouch": [
        "[slouch]",
        "SLX"
    ],
    "slow": [
        "['sloh']",
        "SL"
    ],
    "slowed": [
        "['sloh', 'ed']",
        "SLT"
    ],
    "slower": [
        "['sloh', 'er']",
        "SLR"
    ],
    "slowing": [
        "['sloh', 'ing']",
        "SLNK"
    ],
    "slowly": [
        "['sloh', 'lee']",
        "SLL"
    ],
    "slug": [
        "['sluhg']",
        "SLK"
    ],
    "slugged": [
        "[sluhg,ged]",
        "SLKT"
    ],
    "slugging": [
        "[sluhg,ging]",
        "SLKNK"
    ],
    "slugs": [
        "['sluhg', 's']",
        "SLKS"
    ],
    "slum": [
        "['sluhm']",
        "SLM"
    ],
    "slumber": [
        "['sluhm', 'ber']",
        "SLMPR"
    ],
    "slump": [
        "['sluhmp']",
        "SLMP"
    ],
    "slumped": [
        "['sluhmp', 'ed']",
        "SLMPT"
    ],
    "slums": [
        "['sluhm', 's']",
        "SLMS"
    ],
    "slung": [
        "[sluhng]",
        "SLNK"
    ],
    "slur": [
        "[slur]",
        "SLR"
    ],
    "slurp": [
        "['slurp']",
        "SLRP"
    ],
    "slurping": [
        "['slurp', 'ing']",
        "SLRPNK"
    ],
    "slurred": [
        "[slur,red]",
        "SLRT"
    ],
    "slurring": [
        "[slur,ring]",
        "SLRNK"
    ],
    "slut": [
        "['sluht']",
        "SLT"
    ],
    "sluts": [
        "['sluht', 's']",
        "SLTS"
    ],
    "slutty": [
        "['sluht', 'ee']",
        "SLT"
    ],
    "smack": [
        "['smak']",
        "SMK"
    ],
    "smacked": [
        "['smak', 'ed']",
        "SMKT"
    ],
    "smacking": [
        "['smak', 'ing']",
        "SMKNK"
    ],
    "small": [
        "['smawl']",
        "SML"
    ],
    "smaller": [
        "['smawl', 'er']",
        "SMLR"
    ],
    "smallest": [
        "[smawl,est]",
        "SMLST"
    ],
    "smalls": [
        "[smawlz]",
        "SMLS"
    ],
    "smart": [
        "['smahrt']",
        "SMRT"
    ],
    "smarter": [
        "['smahrt', 'er']",
        "SMRTR"
    ],
    "smartest": [
        "['smahrt', 'est']",
        "SMRTST"
    ],
    "smarts": [
        "[smahrt,s]",
        "SMRTS"
    ],
    "smash": [
        "['smash']",
        "SMX"
    ],
    "smashed": [
        "['smasht']",
        "SMXT"
    ],
    "smashing": [
        "['smash', 'ing']",
        "SMXNK"
    ],
    "smear": [
        "['smeer']",
        "SMR"
    ],
    "smell": [
        "['smel']",
        "SML"
    ],
    "smelled": [
        "['smel', 'ed']",
        "SMLT"
    ],
    "smelling": [
        "['smel', 'ing']",
        "SMLNK"
    ],
    "smells": [
        "[smel,s]",
        "SMLS"
    ],
    "smelly": [
        "['smel', 'ee']",
        "SML"
    ],
    "smile": [
        "['smahyl']",
        "SML"
    ],
    "smiles": [
        "[smahyl,s]",
        "SMLS"
    ],
    "smiley": [
        "['smahy', 'lee']",
        "SML"
    ],
    "smirk": [
        "[smurk]",
        "SMRK"
    ],
    "smith": [
        "['smith']",
        "SM0"
    ],
    "smithereens": [
        "[smith,uh,reenz]",
        "SM0RNS"
    ],
    "smoke": [
        "['smohk']",
        "SMK"
    ],
    "smoked": [
        "['smohk', 'd']",
        "SMKT"
    ],
    "smoker": [
        "['smoh', 'ker']",
        "SMKR"
    ],
    "smokers": [
        "[smoh,ker,s]",
        "SMKRS"
    ],
    "smokes": [
        "['smohk', 's']",
        "SMKS"
    ],
    "smooches": [
        "[smooch,es]",
        "SMXS"
    ],
    "smooth": [
        "['smooth']",
        "SM0"
    ],
    "smoother": [
        "[smooth,er]",
        "SM0R"
    ],
    "smoothest": [
        "[smooth,est]",
        "SM0ST"
    ],
    "smoothie": [
        "['smoo', 'thee']",
        "SM0"
    ],
    "smother": [
        "['smuhth', 'er']",
        "SM0R"
    ],
    "smothered": [
        "[smuhth,er,ed]",
        "SM0RT"
    ],
    "smugglers": [
        "[smuhg,uhl,rs]",
        "SMKLRS"
    ],
    "snack": [
        "['snak']",
        "SNK"
    ],
    "snacks": [
        "['snak', 's']",
        "SNKS"
    ],
    "snail": [
        "[sneyl]",
        "SNL"
    ],
    "snails": [
        "['sneyl', 's']",
        "SNLS"
    ],
    "snake": [
        "['sneyk']",
        "SNK"
    ],
    "snakes": [
        "['sneyk', 's']",
        "SNKS"
    ],
    "snaking": [
        [
            "sney",
            "ing"
        ],
        "SNKNK"
    ],
    "snap": [
        "['snap']",
        "SNP"
    ],
    "snapchat": [
        "['snap', 'chat']",
        "SNPXT"
    ],
    "snapped": [
        "[snap,ped]",
        "SNPT"
    ],
    "snapping": [
        "['snap', 'ping']",
        "SNPNK"
    ],
    "snappy": [
        "[snap,ee]",
        "SNP"
    ],
    "snaps": [
        "[snap,s]",
        "SNPS"
    ],
    "snare": [
        "['snair']",
        "SNR"
    ],
    "snares": [
        "['snair', 's']",
        "SNRS"
    ],
    "snatch": [
        "['snach']",
        "SNX"
    ],
    "snatched": [
        "['snach', 'ed']",
        "SNXT"
    ],
    "snatcher": [
        "[snach,er]",
        "SNXR"
    ],
    "snatchers": [
        "[snach,ers]",
        "SNXRS"
    ],
    "snatching": [
        "['snach', 'ing']",
        "SNXNK"
    ],
    "sneak": [
        "['sneek']",
        "SNK"
    ],
    "sneaker": [
        "[snee,ker]",
        "SNKR"
    ],
    "sneakers": [
        "['snee', 'ker', 's']",
        "SNKRS"
    ],
    "sneaking": [
        "['snee', 'king']",
        "SNKNK"
    ],
    "sneaks": [
        "[sneek,s]",
        "SNKS"
    ],
    "sneaky": [
        "['snee', 'kee']",
        "SNK"
    ],
    "sneeze": [
        "['sneez']",
        "SNS"
    ],
    "sneezed": [
        "[sneez,d]",
        "SNST"
    ],
    "snicker": [
        "[snik,er]",
        "SNKR"
    ],
    "snickers": [
        "['snik', 'er', 's']",
        "SNKRS"
    ],
    "sniff": [
        "['snif']",
        "SNF"
    ],
    "sniffing": [
        "['snif', 'ing']",
        "SNFNK"
    ],
    "snipe": [
        "['snahyp']",
        "SNP"
    ],
    "sniper": [
        "['snahyp', 'r']",
        "SNPR"
    ],
    "snipers": [
        "['snahyp', 'rs']",
        "SNPRS"
    ],
    "snitch": [
        "['snich']",
        "SNX"
    ],
    "snitched": [
        "['snich', 'ed']",
        "SNXT"
    ],
    "snitches": [
        "['snich', 'es']",
        "SNXS"
    ],
    "snitching": [
        "['snich', 'ing']",
        "SNXNK"
    ],
    "snobby": [
        "['snob', 'ee']",
        "SNP"
    ],
    "snoop": [
        "['snoop']",
        "SNP"
    ],
    "snoopy": [
        "[snoo,pee]",
        "SNP"
    ],
    "snooze": [
        "['snooz']",
        "SNS"
    ],
    "snore": [
        "[snawr]",
        "SNR"
    ],
    "snort": [
        "['snawrt']",
        "SNRT"
    ],
    "snorter": [
        "['snawr', 'ter']",
        "SNRTR"
    ],
    "snorting": [
        "['snawrt', 'ing']",
        "SNRTNK"
    ],
    "snot": [
        "['snot']",
        "SNT"
    ],
    "snotty": [
        "[snot,ee]",
        "SNT"
    ],
    "snow": [
        "['snoh']",
        "SN"
    ],
    "snowball": [
        "[snoh,bawl]",
        "SNPL"
    ],
    "snowed": [
        "['snoh', 'ed']",
        "SNT"
    ],
    "snowflake": [
        "[snoh,fleyk]",
        "SNFLK"
    ],
    "snowflakes": [
        "[snoh,fleyk,s]",
        "SNFLKS"
    ],
    "snowing": [
        "['snoh', 'ing']",
        "SNNK"
    ],
    "snowman": [
        "['snoh', 'man']",
        "SNMN"
    ],
    "snowy": [
        "[snoh,ee]",
        "SN"
    ],
    "snub": [
        "['snuhb']",
        "SNP"
    ],
    "snuck": [
        "['snuhk']",
        "SNK"
    ],
    "snug": [
        "[snuhg]",
        "SNK"
    ],
    "snuggle": [
        "[snuhg,uhl]",
        "SNKL"
    ],
    "so": [
        "['soh']",
        "S"
    ],
    "so's": [
        "[soh,'s]",
        "SS"
    ],
    "soak": [
        "[sohk]",
        "SK"
    ],
    "soaked": [
        "['sohk', 'ed']",
        "SKT"
    ],
    "soaker": [
        "[sohk,er]",
        "SKR"
    ],
    "soaking": [
        "['sohk', 'ing']",
        "SKNK"
    ],
    "soap": [
        "['sohp']",
        "SP"
    ],
    "soar": [
        "[sawr]",
        "SR"
    ],
    "soaring": [
        "['sawr', 'ing']",
        "SRNK"
    ],
    "sober": [
        "['soh', 'ber']",
        "SPR"
    ],
    "sobriety": [
        "['suh', 'brahy', 'i', 'tee']",
        "SPRT"
    ],
    "soccer": [
        "['sok', 'er']",
        "SXR"
    ],
    "social": [
        "['soh', 'shuhl']",
        "SSL"
    ],
    "socialite": [
        "[soh,shuh,lahyt]",
        "SSLT"
    ],
    "socialize": [
        "['soh', 'shuh', 'lahyz']",
        "SSLS"
    ],
    "society": [
        "['suh', 'sahy', 'i', 'tee']",
        "SST"
    ],
    "sock": [
        "['sok']",
        "SK"
    ],
    "socked": [
        "[sok,ed]",
        "SKT"
    ],
    "socket": [
        "['sok', 'it']",
        "SKT"
    ],
    "sockets": [
        "[sok,it,s]",
        "SKTS"
    ],
    "socks": [
        "['sok', 's']",
        "SKS"
    ],
    "socrates": [
        "[sok,ruh,teez]",
        "SKRTS"
    ],
    "soda": [
        "['soh', 'duh']",
        "ST"
    ],
    "sodas": [
        "['soh', 'duh', 's']",
        "STS"
    ],
    "sofa": [
        "['soh', 'fuh']",
        "SF"
    ],
    "soft": [
        "['sawft']",
        "SFT"
    ],
    "softball": [
        "[sawft,bawl]",
        "SFTPL"
    ],
    "soften": [
        "[saw,fuhn]",
        "SFTN"
    ],
    "softer": [
        "['sawft', 'er']",
        "SFTR"
    ],
    "softly": [
        "['sawft', 'ly']",
        "SFTL"
    ],
    "soho": [
        "['soh', 'hoh']",
        "SH"
    ],
    "soil": [
        "['soil']",
        "SL"
    ],
    "solar": [
        "['soh', 'ler']",
        "SLR"
    ],
    "sold": [
        "['sohld']",
        "SLT"
    ],
    "soldier": [
        "['sohl', 'jer']",
        "SLT"
    ],
    "soldiers": [
        "['sohl', 'jer', 's']",
        "SLTRS"
    ],
    "sole": [
        "[sohl]",
        "SL"
    ],
    "solemnly": [
        "['sol', 'uhm', 'ly']",
        "SLMNL"
    ],
    "soles": [
        "['Spanishsaw', 'les']",
        "SLS"
    ],
    "solid": [
        "['sol', 'id']",
        "SLT"
    ],
    "solitaire": [
        "['sol', 'i', 'tair']",
        "SLTR"
    ],
    "solitaires": [
        "['sol', 'i', 'tair', 's']",
        "SLTRS"
    ],
    "solo": [
        "['soh', 'loh']",
        "SL"
    ],
    "solution": [
        "[suh,loo,shuhn]",
        "SLXN"
    ],
    "solutions": [
        "[suh,loo,shuhn,s]",
        "SLXNS"
    ],
    "solve": [
        "['solv']",
        "SLF"
    ],
    "solved": [
        "[solv,d]",
        "SLFT"
    ],
    "solving": [
        [
            "solv",
            "ing"
        ],
        "SLFNK"
    ],
    "some": [
        "['suhm']",
        "SM"
    ],
    "somebody": [
        "['suhm', 'bod', 'ee']",
        "SMPT"
    ],
    "somebody's": [
        "[suhm,bod,ee,'s]",
        "SMPTS"
    ],
    "someday": [
        "['suhm', 'dey']",
        "SMT"
    ],
    "somehow": [
        "[suhm,hou]",
        "SMH"
    ],
    "someone": [
        "['suhm', 'wuhn']",
        "SMN"
    ],
    "someone's": [
        "['suhm', 'wuhn', \"'s\"]",
        "SMNS"
    ],
    "something": [
        "['suhm', 'thing']",
        "SM0NK"
    ],
    "sometime": [
        "[suhm,tahym]",
        "SMTM"
    ],
    "sometimes": [
        "['suhm', 'tahymz']",
        "SMTMS"
    ],
    "somewhat": [
        "[suhm,hwuht]",
        "SMT"
    ],
    "somewhere": [
        "['suhm', 'hwair']",
        "SMR"
    ],
    "son": [
        "['suhn']",
        "SN"
    ],
    "son's": [
        "['suhn', \"'s\"]",
        "SNNS"
    ],
    "song": [
        "['sawng']",
        "SNK"
    ],
    "song's": [
        "[sawng,'s]",
        "SNKKS"
    ],
    "songs": [
        "['sawng', 's']",
        "SNKS"
    ],
    "sonic": [
        "['son', 'ik']",
        "SNK"
    ],
    "sonny": [
        "['suhn', 'ee']",
        "SN"
    ],
    "sons": [
        "['suhn', 's']",
        "SNS"
    ],
    "soon": [
        "['soon']",
        "SN"
    ],
    "sooner": [
        "['soo', 'ner']",
        "SNR"
    ],
    "soothe": [
        "[sooth]",
        "S0"
    ],
    "sophisticated": [
        "['suh', 'fis', 'ti', 'key', 'tid']",
        "SFSTKTT"
    ],
    "sophomore": [
        "[sof,uh,mawr]",
        "SFMR"
    ],
    "soprano": [
        "['suh', 'pran', 'oh']",
        "SPRN"
    ],
    "sore": [
        "['sawr']",
        "SR"
    ],
    "sorrow": [
        "['sor', 'oh']",
        "SR"
    ],
    "sorry": [
        "['sor', 'ee']",
        "SR"
    ],
    "sort": [
        "['sawrt']",
        "SRT"
    ],
    "sorta": [
        "['sawr', 'tuh']",
        "SRT"
    ],
    "sorted": [
        "['sawr', 'tid']",
        "SRTT"
    ],
    "sorting": [
        "['sawr', 'ting']",
        "SRTNK"
    ],
    "sorts": [
        "[sawrt,s]",
        "SRTS"
    ],
    "sos": [
        "[soh]",
        "SS"
    ],
    "soul": [
        "['sohl']",
        "SL"
    ],
    "soulful": [
        "[sohl,fuhl]",
        "SLFL"
    ],
    "souls": [
        "['sohl', 's']",
        "SLS"
    ],
    "sound": [
        "['sound']",
        "SNT"
    ],
    "sounded": [
        "['sound', 'ed']",
        "SNTT"
    ],
    "sounding": [
        "['soun', 'ding']",
        "SNTNK"
    ],
    "sounds": [
        "['sound', 's']",
        "SNTS"
    ],
    "soundtrack": [
        "[sound,trak]",
        "SNTRK"
    ],
    "soup": [
        "['soop']",
        "SP"
    ],
    "sour": [
        "['souuhr']",
        "SR"
    ],
    "source": [
        "['sawrs']",
        "SRS"
    ],
    "sources": [
        "[sawrs,s]",
        "SRSS"
    ],
    "south": [
        "['noun']",
        "S0"
    ],
    "south's": [
        "[noun,'s]",
        "S00"
    ],
    "southern": [
        "['suhth', 'ern']",
        "S0RN"
    ],
    "southerner": [
        "[suhth,er,ner]",
        "S0RNR"
    ],
    "southpaw": [
        "[south,paw]",
        "S0P"
    ],
    "southwest": [
        "['south', 'west']",
        "S0ST"
    ],
    "souvenir": [
        "[soo,vuh,neer]",
        "SFNR"
    ],
    "sow": [
        "[soh]",
        "S"
    ],
    "soy": [
        "[soi]",
        "S"
    ],
    "spa": [
        "[spah]",
        "SP"
    ],
    "space": [
        "['speys']",
        "SPS"
    ],
    "spaced": [
        "[speys,d]",
        "SPST"
    ],
    "spaces": [
        "['speys', 's']",
        "SPSS"
    ],
    "spaceship": [
        "['speys', 'ship']",
        "SPSXP"
    ],
    "spaceships": [
        "[speys,ship,s]",
        "SPSXPS"
    ],
    "spacious": [
        "[spey,shuhs]",
        "SPSS"
    ],
    "spade": [
        "['speyd']",
        "SPT"
    ],
    "spades": [
        "['speyd', 's']",
        "SPTS"
    ],
    "spaghetti": [
        "['spuh', 'get', 'ee']",
        "SPKT"
    ],
    "spain": [
        "[speyn]",
        "SPN"
    ],
    "spam": [
        "[spam]",
        "SPM"
    ],
    "span": [
        "[span]",
        "SPN"
    ],
    "spangled": [
        "[spang,guhl,d]",
        "SPNKLT"
    ],
    "spanish": [
        "['span', 'ish']",
        "SPNX"
    ],
    "spank": [
        "[spangk]",
        "SPNK"
    ],
    "spanked": [
        "[spangk,ed]",
        "SPNKT"
    ],
    "spanking": [
        "['spang', 'king']",
        "SPNKNK"
    ],
    "spar": [
        "['spahr']",
        "SPR"
    ],
    "spare": [
        "['spair']",
        "SPR"
    ],
    "sparing": [
        "['spair', 'ing']",
        "SPRNK"
    ],
    "spark": [
        "['spahrk']",
        "SPRK"
    ],
    "sparking": [
        "[spahrk,ing]",
        "SPRKNK"
    ],
    "sparkle": [
        "[spahr,kuhl]",
        "SPRKL"
    ],
    "sparkles": [
        "['spahr', 'kuhl', 's']",
        "SPRKLS"
    ],
    "sparks": [
        "['spahrks']",
        "SPRKS"
    ],
    "sparring": [
        "[spahr,ring]",
        "SPRNK"
    ],
    "sparrow": [
        "[spar,oh]",
        "SPR"
    ],
    "spas": [
        "['spah', 's']",
        "SPS"
    ],
    "spat": [
        "[spat]",
        "SPT"
    ],
    "spatula": [
        "[spach,uh,luh]",
        "SPTL"
    ],
    "spaz": [
        "['spaz']",
        "SPS"
    ],
    "speak": [
        "['speek']",
        "SPK"
    ],
    "speaker": [
        "['spee', 'ker']",
        "SPKR"
    ],
    "speakers": [
        "['spee', 'ker', 's']",
        "SPKRS"
    ],
    "speaking": [
        "['spee', 'king']",
        "SPKNK"
    ],
    "speaks": [
        "[speek,s]",
        "SPKS"
    ],
    "spears": [
        "['speer', 's']",
        "SPRS"
    ],
    "special": [
        "['spesh', 'uhl']",
        "SPSL"
    ],
    "specialize": [
        "[spesh,uh,lahyz]",
        "SPSLS"
    ],
    "specially": [
        "[spesh,uhl,ly]",
        "SPSL"
    ],
    "species": [
        "['spee', 'sheez']",
        "SPSS"
    ],
    "specific": [
        "['spi', 'sif', 'ik']",
        "SPSFK"
    ],
    "specifically": [
        "[spi,sif,ik,lee]",
        "SPSFKL"
    ],
    "specs": [
        "['speks']",
        "SPKS"
    ],
    "spectacular": [
        "['spek', 'tak', 'yuh', 'ler']",
        "SPKTKLR"
    ],
    "speculation": [
        "['spek', 'yuh', 'ley', 'shuhn']",
        "SPKLXN"
    ],
    "sped": [
        "[sped]",
        "SPT"
    ],
    "speech": [
        "['speech']",
        "SPX"
    ],
    "speeches": [
        "[speech,es]",
        "SPXS"
    ],
    "speechless": [
        "[speech,lis]",
        "SPKLS"
    ],
    "speed": [
        "['speed']",
        "SPT"
    ],
    "speedboat": [
        "[speed,boht]",
        "SPTPT"
    ],
    "speeding": [
        "['spee', 'ding']",
        "SPTNK"
    ],
    "speedy": [
        "['spee', 'dee']",
        "SPT"
    ],
    "spell": [
        "['spel']",
        "SPL"
    ],
    "spelled": [
        "[spel,ed]",
        "SPLT"
    ],
    "spelling": [
        "['spel', 'ing']",
        "SPLNK"
    ],
    "spells": [
        "[spel,s]",
        "SPLS"
    ],
    "spend": [
        "['spend']",
        "SPNT"
    ],
    "spender": [
        "[spen,der]",
        "SPNTR"
    ],
    "spenders": [
        "[spen,der,s]",
        "SPNTRS"
    ],
    "spending": [
        "['spend', 'ing']",
        "SPNTNK"
    ],
    "spent": [
        "['spent']",
        "SPNT"
    ],
    "sperm": [
        "['spurm']",
        "SPRM"
    ],
    "spew": [
        "[spyoo]",
        "SP"
    ],
    "sphinx": [
        "['sfingks']",
        "SFNKS"
    ],
    "spice": [
        "['spahys']",
        "SPS"
    ],
    "spider": [
        "['spahy', 'der']",
        "SPTR"
    ],
    "spiders": [
        "['spahy', 'der', 's']",
        "SPTRS"
    ],
    "spiffy": [
        "[spif,ee]",
        "SPF"
    ],
    "spike": [
        "['spahyk']",
        "SPK"
    ],
    "spiked": [
        "[spahyk,d]",
        "SPKT"
    ],
    "spikes": [
        "['spahyk', 's']",
        "SPKS"
    ],
    "spill": [
        "['spil']",
        "SPL"
    ],
    "spilled": [
        "['spil', 'ed']",
        "SPLT"
    ],
    "spilling": [
        "['spil', 'ing']",
        "SPLNK"
    ],
    "spills": [
        "[spil,s]",
        "SPLS"
    ],
    "spilt": [
        "['spilt']",
        "SPLT"
    ],
    "spin": [
        "['spin']",
        "SPN"
    ],
    "spinach": [
        "[spin,ich]",
        "SPNK"
    ],
    "spine": [
        "['spahyn']",
        "SPN"
    ],
    "spinner": [
        "['spin', 'er']",
        "SPNR"
    ],
    "spinners": [
        "[spin,er,s]",
        "SPNRS"
    ],
    "spinning": [
        "['spin', 'ing']",
        "SPNNK"
    ],
    "spins": [
        "[spin,s]",
        "SPNS"
    ],
    "spirit": [
        "['spir', 'it']",
        "SPRT"
    ],
    "spirits": [
        "[spir,it,s]",
        "SPRTS"
    ],
    "spiritual": [
        "[spir,i,choo,uhl]",
        "SPRTL"
    ],
    "spiritually": [
        "['spir', 'i', 'choo', 'uhl', 'ly']",
        "SPRTL"
    ],
    "spit": [
        "['spit']",
        "SPT"
    ],
    "spite": [
        "[spahyt]",
        "SPT"
    ],
    "spiteful": [
        "['spahyt', 'fuhl']",
        "SPTFL"
    ],
    "spits": [
        "['spit', 's']",
        "SPTS"
    ],
    "spitted": [
        "[spit,ted]",
        "SPTT"
    ],
    "spitter": [
        "[spit,er]",
        "SPTR"
    ],
    "spitting": [
        "['spit', 'ting']",
        "SPTNK"
    ],
    "splash": [
        "['splash']",
        "SPLX"
    ],
    "splashed": [
        "[splash,ed]",
        "SPLXT"
    ],
    "splashing": [
        "['splash', 'ing']",
        "SPLXNK"
    ],
    "splat": [
        "[splat]",
        "SPLT"
    ],
    "splatter": [
        "[splat,er]",
        "SPLTR"
    ],
    "splattered": [
        "['splat', 'er', 'ed']",
        "SPLTRT"
    ],
    "spleen": [
        "['spleen']",
        "SPLN"
    ],
    "splendid": [
        "[splen,did]",
        "SPLNTT"
    ],
    "spliff": [
        "['splif']",
        "SPLF"
    ],
    "spliffs": [
        "[splif,s]",
        "SPLFS"
    ],
    "split": [
        "['split']",
        "SPLT"
    ],
    "splits": [
        "['split', 's']",
        "SPLTS"
    ],
    "splitting": [
        "[split,ing]",
        "SPLTNK"
    ],
    "splurge": [
        "['splurj']",
        "SPLRJ"
    ],
    "spock": [
        "[spok]",
        "SPK"
    ],
    "spoil": [
        "['spoil']",
        "SPL"
    ],
    "spoiled": [
        "['spoil', 'ed']",
        "SPLT"
    ],
    "spoke": [
        "['spohk']",
        "SPK"
    ],
    "spoken": [
        "[spoh,kuhn]",
        "SPKN"
    ],
    "spokes": [
        "['spohk', 's']",
        "SPKS"
    ],
    "sponsor": [
        "['spon', 'ser']",
        "SPNSR"
    ],
    "sponsored": [
        "['spon', 'ser', 'ed']",
        "SPNSRT"
    ],
    "spontaneous": [
        "[spon,tey,nee,uhs]",
        "SPNTNS"
    ],
    "spoof": [
        "[spoof]",
        "SPF"
    ],
    "spook": [
        "[spook]",
        "SPK"
    ],
    "spooked": [
        "['spook', 'ed']",
        "SPKT"
    ],
    "spoon": [
        "['spoon']",
        "SPN"
    ],
    "spooning": [
        "['spoon', 'ing']",
        "SPNNK"
    ],
    "sport": [
        "['spawrt']",
        "SPRT"
    ],
    "sporting": [
        "[spawr,ting]",
        "SPRTNK"
    ],
    "sports": [
        "['spawrts']",
        "SPRTS"
    ],
    "sporty": [
        "[spawr,tee]",
        "SPRT"
    ],
    "spot": [
        "['spot']",
        "SPT"
    ],
    "spotlight": [
        "['spot', 'lahyt']",
        "SPTLT"
    ],
    "spotlights": [
        "[spot,lahyt,s]",
        "SPTLTS"
    ],
    "spots": [
        "['spot', 's']",
        "SPTS"
    ],
    "spotted": [
        "[spot,id]",
        "SPTT"
    ],
    "spotting": [
        "[spot,ting]",
        "SPTNK"
    ],
    "spouse": [
        "['nounspous']",
        "SPS"
    ],
    "spout": [
        "[spout]",
        "SPT"
    ],
    "sprain": [
        "[spreyn]",
        "SPRN"
    ],
    "sprained": [
        "['spreyn', 'ed']",
        "SPRNT"
    ],
    "spray": [
        "['sprey']",
        "SPR"
    ],
    "sprayed": [
        "[sprey,ed]",
        "SPRT"
    ],
    "spraying": [
        "['sprey', 'ing']",
        "SPRNK"
    ],
    "spread": [
        "['spred']",
        "SPRT"
    ],
    "spreading": [
        "['spred', 'ing']",
        "SPRTNK"
    ],
    "spree": [
        "['spree']",
        "SPR"
    ],
    "sprees": [
        "['spree', 's']",
        "SPRS"
    ],
    "spring": [
        "['spring']",
        "SPRNK"
    ],
    "springer": [
        "['spring', 'er']",
        "SPRNKR"
    ],
    "springs": [
        "[springz]",
        "SPRNKS"
    ],
    "sprinkle": [
        "['spring', 'kuhl']",
        "SPRNKL"
    ],
    "sprinkled": [
        "['spring', 'kuhl', 'd']",
        "SPRNKLT"
    ],
    "sprinkler": [
        "['spring', 'kler']",
        "SPRNKLR"
    ],
    "sprinklers": [
        "[spring,kler,s]",
        "SPRNKLRS"
    ],
    "sprinkles": [
        "['spring', 'kuhl', 's']",
        "SPRNKLS"
    ],
    "sprint": [
        "[sprint]",
        "SPRNT"
    ],
    "sprinter": [
        "['sprint', 'er']",
        "SPRNTR"
    ],
    "sprinting": [
        "['sprint', 'ing']",
        "SPRNTNK"
    ],
    "sprite": [
        "['sprahyt']",
        "SPRT"
    ],
    "sprung": [
        "['spruhng']",
        "SPRNK"
    ],
    "spud": [
        "[spuhd]",
        "SPT"
    ],
    "spun": [
        "[spuhn]",
        "SPN"
    ],
    "spur": [
        "['spur']",
        "SPR"
    ],
    "spurs": [
        "[spur,s]",
        "SPRS"
    ],
    "spurts": [
        "[spurt,s]",
        "SPRTS"
    ],
    "spy": [
        "['spahy']",
        "SP"
    ],
    "spying": [
        "[spahy,ing]",
        "SPNK"
    ],
    "squad": [
        "['skwod']",
        "SKT"
    ],
    "square": [
        "['skwair']",
        "SKR"
    ],
    "squares": [
        "['skwair', 's']",
        "SKRS"
    ],
    "squash": [
        "['skwosh']",
        "SKX"
    ],
    "squat": [
        "['skwot']",
        "SKT"
    ],
    "squeak": [
        "['skweek']",
        "SKK"
    ],
    "squeaking": [
        "['skweek', 'ing']",
        "SKKNK"
    ],
    "squeal": [
        "['skweel']",
        "SKL"
    ],
    "squeeze": [
        "['skweez']",
        "SKS"
    ],
    "squeezed": [
        "[skweez,d]",
        "SKST"
    ],
    "squirrel": [
        "['skwur', 'uhl']",
        "SKRL"
    ],
    "squirt": [
        "['skwurt']",
        "SKRT"
    ],
    "squirting": [
        "['skwurt', 'ing']",
        "SKRTNK"
    ],
    "ss": [
        "[es]",
        "S"
    ],
    "stab": [
        "['stab']",
        "STP"
    ],
    "stabbed": [
        "[stab,bed]",
        "STPT"
    ],
    "stabbing": [
        "['stab', 'ing']",
        "STPNK"
    ],
    "stable": [
        "['stey', 'buhl']",
        "STPL"
    ],
    "stacey": [
        "['stey', 'see']",
        "STS"
    ],
    "stack": [
        "['stak']",
        "STK"
    ],
    "stacked": [
        "['stakt']",
        "STKT"
    ],
    "stacking": [
        "['stak', 'ing']",
        "STKNK"
    ],
    "stacks": [
        "['stak', 's']",
        "STKS"
    ],
    "stadium": [
        "[stey,dee,uhm]",
        "STTM"
    ],
    "stadiums": [
        "['stey', 'dee', 'uhm', 's']",
        "STTMS"
    ],
    "staff": [
        "['staf']",
        "STF"
    ],
    "stage": [
        "['steyj']",
        "STJ"
    ],
    "staged": [
        "['steyjd']",
        "STJT"
    ],
    "stages": [
        "[steyj,s]",
        "STJS"
    ],
    "stagnant": [
        "[stag,nuhnt]",
        "STNNT"
    ],
    "stain": [
        "['steyn']",
        "STN"
    ],
    "stained": [
        "['steyn', 'ed']",
        "STNT"
    ],
    "stainless": [
        "['steyn', 'lis']",
        "STNLS"
    ],
    "stains": [
        "['steyn', 's']",
        "STNS"
    ],
    "staircase": [
        "[stair,keys]",
        "STRKS"
    ],
    "stairs": [
        "['stair', 's']",
        "STRS"
    ],
    "stake": [
        "['steyk']",
        "STK"
    ],
    "stakes": [
        "['steyk', 's']",
        "STKS"
    ],
    "stale": [
        "['steyl']",
        "STL"
    ],
    "stalk": [
        "['stawk']",
        "STLK"
    ],
    "stalker": [
        "[staw,ker]",
        "STLKR"
    ],
    "stalking": [
        "['staw', 'king']",
        "STLKNK"
    ],
    "stall": [
        "['stawl']",
        "STL"
    ],
    "stalling": [
        "['stawl', 'ing']",
        "STLNK"
    ],
    "stallion": [
        "['stal', 'yuhn']",
        "STLN"
    ],
    "stamina": [
        "['stam', 'uh', 'nuh']",
        "STMN"
    ],
    "stamp": [
        "['stamp']",
        "STMP"
    ],
    "stamped": [
        "[stamp,ed]",
        "STMPT"
    ],
    "stamps": [
        "['stamp', 's']",
        "STMPS"
    ],
    "stan": [
        "['stan']",
        "STN"
    ],
    "stance": [
        "[stans]",
        "STNS"
    ],
    "stand": [
        "['stand']",
        "STNT"
    ],
    "standard": [
        "[stan,derd]",
        "STNTRT"
    ],
    "standards": [
        "['stan', 'derd', 's']",
        "STNTRTS"
    ],
    "standby": [
        "[stand,bahy]",
        "STNTP"
    ],
    "standing": [
        "['stan', 'ding']",
        "STNTNK"
    ],
    "standoff": [
        "['stand', 'awf']",
        "STNTF"
    ],
    "stands": [
        "['stand', 's']",
        "STNTS"
    ],
    "stank": [
        "['stangk']",
        "STNK"
    ],
    "stanky": [
        [
            "stangk",
            "ee"
        ],
        "STNK"
    ],
    "stanley": [
        "['stan', 'lee']",
        "STNL"
    ],
    "staple": [
        "[stey,puhl]",
        "STPL"
    ],
    "staples": [
        "['stey', 'puhl', 's']",
        "STPLS"
    ],
    "star": [
        "['stahr']",
        "STR"
    ],
    "starburst": [
        "['stahr', 'burst']",
        "STRPRST"
    ],
    "starch": [
        "['stahrch']",
        "STRX"
    ],
    "stardom": [
        "['stahr', 'duhm']",
        "STRTM"
    ],
    "stare": [
        "['stair']",
        "STR"
    ],
    "stared": [
        "['stair', 'd']",
        "STRT"
    ],
    "stares": [
        "['stair', 's']",
        "STRS"
    ],
    "starfish": [
        "[stahr,fish]",
        "STRFX"
    ],
    "stark": [
        "['stahrk']",
        "STRK"
    ],
    "starring": [
        "[stahr,ring]",
        "STRNK"
    ],
    "stars": [
        "['stahr', 's']",
        "STRS"
    ],
    "start": [
        "['stahrt']",
        "STRT"
    ],
    "started": [
        "['stahrt', 'ed']",
        "STRTT"
    ],
    "starter": [
        "['stahr', 'ter']",
        "STRTR"
    ],
    "starters": [
        "[stahr,ter,s]",
        "STRTRS"
    ],
    "starting": [
        "['stahrt', 'ing']",
        "STRTNK"
    ],
    "starts": [
        "['stahrt', 's']",
        "STRTS"
    ],
    "starve": [
        "[stahrv]",
        "STRF"
    ],
    "starved": [
        "[stahrv,d]",
        "STRFT"
    ],
    "starving": [
        [
            "stahrv",
            "ing"
        ],
        "STRFNK"
    ],
    "stash": [
        "['stash']",
        "STX"
    ],
    "stashed": [
        "['stash', 'ed']",
        "STXT"
    ],
    "stashes": [
        "[stash,es]",
        "STXS"
    ],
    "stashing": [
        "['stash', 'ing']",
        "STXNK"
    ],
    "state": [
        "['steyt']",
        "STT"
    ],
    "statement": [
        "['steyt', 'muhnt']",
        "STTMNT"
    ],
    "statements": [
        "['steyt', 'muhnt', 's']",
        "STTMNTS"
    ],
    "states": [
        "['steyt', 's']",
        "STTS"
    ],
    "static": [
        "['stat', 'ik']",
        "STTK"
    ],
    "station": [
        "['stey', 'shuhn']",
        "STXN"
    ],
    "stations": [
        "['stey', 'shuhn', 's']",
        "STXNS"
    ],
    "statistic": [
        "[stuh,tis,tik]",
        "STTSTK"
    ],
    "statistics": [
        "['stuh', 'tis', 'tiks']",
        "STTSTKS"
    ],
    "stats": [
        "['stat', 's']",
        "STTS"
    ],
    "statue": [
        "[stach,oo]",
        "STT"
    ],
    "statues": [
        "['stach', 'oo', 's']",
        "STTS"
    ],
    "status": [
        "['stey', 'tuhs']",
        "STTS"
    ],
    "statute": [
        "[stach,oot]",
        "STTT"
    ],
    "statutory": [
        "['stach', 'oo', 'tawr', 'ee']",
        "STTTR"
    ],
    "stay": [
        "['stey']",
        "ST"
    ],
    "stayed": [
        "['stey', 'ed']",
        "STT"
    ],
    "staying": [
        "['stey', 'ing']",
        "STNK"
    ],
    "stays": [
        "['stey', 's']",
        "STS"
    ],
    "stead": [
        "[sted]",
        "STT"
    ],
    "steady": [
        "['sted', 'ee']",
        "STT"
    ],
    "steak": [
        "['steyk']",
        "STK"
    ],
    "steaks": [
        "['steyk', 's']",
        "STKS"
    ],
    "steal": [
        "['steel']",
        "STL"
    ],
    "stealing": [
        "['stee', 'ling']",
        "STLNK"
    ],
    "steam": [
        "['steem']",
        "STM"
    ],
    "steamboat": [
        "['steem', 'boht']",
        "STMPT"
    ],
    "steamer": [
        "['stee', 'mer']",
        "STMR"
    ],
    "steaming": [
        "['steem', 'ing']",
        "STMNK"
    ],
    "steel": [
        "['steel']",
        "STL"
    ],
    "steeped": [
        "[steep,ed]",
        "STPT"
    ],
    "steeper": [
        "[steep,er]",
        "STPR"
    ],
    "steer": [
        "['steer']",
        "STR"
    ],
    "steering": [
        "[steer,ing]",
        "STRNK"
    ],
    "stem": [
        "[stem]",
        "STM"
    ],
    "stems": [
        "[stem,s]",
        "STMS"
    ],
    "step": [
        "['step']",
        "STP"
    ],
    "stepped": [
        "['step', 'ped']",
        "STPT"
    ],
    "stepping": [
        "['step', 'ping']",
        "STPNK"
    ],
    "steps": [
        "['step', 's']",
        "STPS"
    ],
    "stereo": [
        "['ster', 'ee', 'oh']",
        "STR"
    ],
    "stereotype": [
        "[ster,ee,uh,tahyp]",
        "STRTP"
    ],
    "sternum": [
        "[stur,nuhm]",
        "STRNM"
    ],
    "steroids": [
        "['steer', 'oid', 's']",
        "STRTS"
    ],
    "steve": [
        "['steev']",
        "STF"
    ],
    "stew": [
        "[stoo]",
        "ST"
    ],
    "stewardess": [
        "['stoo', 'er', 'dis']",
        "STRTS"
    ],
    "stewart": [
        "['stoo', 'ert']",
        "STRT"
    ],
    "stick": [
        "['stik']",
        "STK"
    ],
    "sticker": [
        "[stik,er]",
        "STKR"
    ],
    "stickers": [
        "[stik,er,s]",
        "STKRS"
    ],
    "sticking": [
        "['stik', 'ing']",
        "STKNK"
    ],
    "sticks": [
        "['stik', 's']",
        "STKS"
    ],
    "sticky": [
        "['stik', 'ee']",
        "STK"
    ],
    "stiff": [
        "['stif']",
        "STF"
    ],
    "stilettos": [
        "[sti,let,oh,s]",
        "STLTS"
    ],
    "still": [
        "['stil']",
        "STL"
    ],
    "sting": [
        "['sting']",
        "STNK"
    ],
    "stinging": [
        "[sting,ing]",
        "STNJNK"
    ],
    "stingray": [
        "['sting', 'rey']",
        "STNKR"
    ],
    "stingy": [
        "['stin', 'jee']",
        "STNK"
    ],
    "stink": [
        "['stingk']",
        "STNK"
    ],
    "stinking": [
        "['sting', 'king']",
        "STNKNK"
    ],
    "stinky": [
        "[sting,kee]",
        "STNK"
    ],
    "stir": [
        "['stur']",
        "STR"
    ],
    "stirring": [
        "[stur,ing]",
        "STRNK"
    ],
    "stitch": [
        "['stich']",
        "STX"
    ],
    "stitched": [
        "['stich', 'ed']",
        "STXT"
    ],
    "stitches": [
        "['stich', 'es']",
        "STXS"
    ],
    "stock": [
        "['stok']",
        "STK"
    ],
    "stocked": [
        "[stok,ed]",
        "STKT"
    ],
    "stocking": [
        "[stok,ing]",
        "STKNK"
    ],
    "stocks": [
        "['stok', 's']",
        "STKS"
    ],
    "stoked": [
        "['stohkt']",
        "STKT"
    ],
    "stokes": [
        "[stohks]",
        "STKS"
    ],
    "stole": [
        "['stohl']",
        "STL"
    ],
    "stolen": [
        "['stoh', 'luhn']",
        "STLN"
    ],
    "stomach": [
        "['stuhm', 'uhk']",
        "STMK"
    ],
    "stomach's": [
        "[stuhm,uhk,'s]",
        "STMKK"
    ],
    "stomachs": [
        "['stuhm', 'uhk', 's']",
        "STMKS"
    ],
    "stomp": [
        "['stomp']",
        "STMP"
    ],
    "stomped": [
        "[stomp,ed]",
        "STMPT"
    ],
    "stomping": [
        "[stomp,ing]",
        "STMPNK"
    ],
    "stone": [
        "['stohn']",
        "STN"
    ],
    "stoned": [
        "['stohnd']",
        "STNT"
    ],
    "stoner": [
        "['stoh', 'ner']",
        "STNR"
    ],
    "stones": [
        "['stohn', 's']",
        "STNS"
    ],
    "stood": [
        "['stood']",
        "STT"
    ],
    "stool": [
        "[stool]",
        "STL"
    ],
    "stoop": [
        "[stoop]",
        "STP"
    ],
    "stop": [
        "['stop']",
        "STP"
    ],
    "stoplight": [
        "['stop', 'lahyt']",
        "STPLT"
    ],
    "stopped": [
        "['stop', 'ped']",
        "STPT"
    ],
    "stopper": [
        "['stop', 'er']",
        "STPR"
    ],
    "stopping": [
        "['stop', 'ing']",
        "STPNK"
    ],
    "stops": [
        "['stop', 's']",
        "STPS"
    ],
    "store": [
        "['stawr']",
        "STR"
    ],
    "store's": [
        "[stawr,'s]",
        "STRS"
    ],
    "stored": [
        "[stawr,d]",
        "STRT"
    ],
    "stores": [
        "['stawr', 's']",
        "STRS"
    ],
    "stork": [
        "['stawrk']",
        "STRK"
    ],
    "storm": [
        "['stawrm']",
        "STRM"
    ],
    "storming": [
        "[stawrm,ing]",
        "STRMNK"
    ],
    "stormy": [
        "[stawr,mee]",
        "STRM"
    ],
    "story": [
        "['stawr', 'ee']",
        "STR"
    ],
    "stove": [
        "['stohv']",
        "STF"
    ],
    "stoves": [
        "['stohv', 's']",
        "STFS"
    ],
    "straddle": [
        "[strad,l]",
        "STRTL"
    ],
    "straight": [
        "['streyt']",
        "STRT"
    ],
    "straighten": [
        "['streyt', 'n']",
        "STRTN"
    ],
    "straightened": [
        "[streyt,n,ed]",
        "STRTNT"
    ],
    "straightjacket": [
        "[streyt,jak,it]",
        "STRTJKT"
    ],
    "strain": [
        "['streyn']",
        "STRN"
    ],
    "straining": [
        "[streyn,ing]",
        "STRNNK"
    ],
    "strait": [
        "[streyt]",
        "STRT"
    ],
    "stranded": [
        "['stran', 'did']",
        "STRNTT"
    ],
    "strange": [
        "['streynj']",
        "STRNJ"
    ],
    "stranger": [
        "['streyn', 'jer']",
        "STRNKR"
    ],
    "strangers": [
        "['streyn', 'jer', 's']",
        "STRNKRS"
    ],
    "strangle": [
        "[strang,guhl]",
        "STRNKL"
    ],
    "strap": [
        "['strap']",
        "STRP"
    ],
    "strapped": [
        "['strapt']",
        "STRPT"
    ],
    "strapping": [
        "[strap,ing]",
        "STRPNK"
    ],
    "straps": [
        "['strap', 's']",
        "STRPS"
    ],
    "straw": [
        "['straw']",
        "STR"
    ],
    "strawberry": [
        "['straw', 'ber', 'ee']",
        "STRPR"
    ],
    "straws": [
        "[straw,s]",
        "STRS"
    ],
    "stray": [
        "['strey']",
        "STR"
    ],
    "streaks": [
        "['streek', 's']",
        "STRKS"
    ],
    "stream": [
        "['streem']",
        "STRM"
    ],
    "street": [
        "['street']",
        "STRT"
    ],
    "street's": [
        "[street,'s]",
        "STRTTS"
    ],
    "streets": [
        "['street', 's']",
        "STRTS"
    ],
    "strength": [
        "[strengkth]",
        "STRNK0"
    ],
    "strep": [
        "[strep]",
        "STRP"
    ],
    "stress": [
        "['stres']",
        "STRS"
    ],
    "stressed": [
        "['stres', 'ed']",
        "STRST"
    ],
    "stressing": [
        "['stres', 'ing']",
        "STRSNK"
    ],
    "stretch": [
        "['strech']",
        "STRX"
    ],
    "stretched": [
        "['strech', 'ed']",
        "STRXT"
    ],
    "stretcher": [
        "[strech,er]",
        "STRXR"
    ],
    "stretches": [
        "[strech,es]",
        "STRXS"
    ],
    "stretching": [
        "['strech', 'ing']",
        "STRXNK"
    ],
    "strict": [
        "['strikt']",
        "STRKT"
    ],
    "strictly": [
        "[strikt,lee]",
        "STRKTL"
    ],
    "stride": [
        "['strahyd']",
        "STRT"
    ],
    "strike": [
        "['strahyk']",
        "STRK"
    ],
    "strikes": [
        "['strahyk', 's']",
        "STRKS"
    ],
    "striking": [
        "['strahy', 'king']",
        "STRKNK"
    ],
    "string": [
        "['string']",
        "STRNK"
    ],
    "strings": [
        "['string', 's']",
        "STRNKS"
    ],
    "strip": [
        "['strip']",
        "STRP"
    ],
    "stripe": [
        "['strahyp']",
        "STRP"
    ],
    "striped": [
        "['strahypt']",
        "STRPT"
    ],
    "stripes": [
        "['strahyp', 's']",
        "STRPS"
    ],
    "stripped": [
        "['stript']",
        "STRPT"
    ],
    "stripper": [
        "['strip', 'er']",
        "STRPR"
    ],
    "strippers": [
        "['strip', 'er', 's']",
        "STRPRS"
    ],
    "stripping": [
        "['strip', 'ping']",
        "STRPNK"
    ],
    "strips": [
        "[strip,s]",
        "STRPS"
    ],
    "strive": [
        "[strahyv]",
        "STRF"
    ],
    "strobe": [
        "[strohb]",
        "STRP"
    ],
    "stroke": [
        "['strohk']",
        "STRK"
    ],
    "strokes": [
        "[strohk,s]",
        "STRKS"
    ],
    "stroll": [
        "[strohl]",
        "STRL"
    ],
    "stroller": [
        "[stroh,ler]",
        "STRLR"
    ],
    "strolling": [
        "[strohl,ing]",
        "STRLNK"
    ],
    "strong": [
        "['strawng']",
        "STRNK"
    ],
    "stronger": [
        "['strawng', 'er']",
        "STRNKR"
    ],
    "strongest": [
        "[strawng,est]",
        "STRNJST"
    ],
    "struck": [
        "[struhk]",
        "STRK"
    ],
    "strudel": [
        "['strood', 'l']",
        "STRTL"
    ],
    "struggle": [
        "['struhg', 'uhl']",
        "STRKL"
    ],
    "struggled": [
        "[struhg,uhl,d]",
        "STRKLT"
    ],
    "strung": [
        "[struhng]",
        "STRNK"
    ],
    "strut": [
        "[struht]",
        "STRT"
    ],
    "stubborn": [
        "[stuhb,ern]",
        "STPRN"
    ],
    "stuck": [
        "['stuhk']",
        "STK"
    ],
    "stud": [
        "['stuhd']",
        "STT"
    ],
    "studded": [
        "['stuhd', 'ded']",
        "STTT"
    ],
    "student": [
        "['stood', 'nt']",
        "STTNT"
    ],
    "students": [
        "[stood,nt,s]",
        "STTNTS"
    ],
    "studied": [
        "['stuhd', 'eed']",
        "STTT"
    ],
    "studio": [
        "['stoo', 'dee', 'oh']",
        "STT"
    ],
    "studios": [
        "[stoo,dee,oh,s]",
        "STTS"
    ],
    "studs": [
        "[stuhd,s]",
        "STTS"
    ],
    "study": [
        "['stuhd', 'ee']",
        "STT"
    ],
    "studying": [
        "['stuhd', 'ee', 'ing']",
        "STTNK"
    ],
    "stuff": [
        "['stuhf']",
        "STF"
    ],
    "stuffed": [
        "['stuhf', 'ed']",
        "STFT"
    ],
    "stuffing": [
        "['stuhf', 'ing']",
        "STFNK"
    ],
    "stumble": [
        "['stuhm', 'buhl']",
        "STMPL"
    ],
    "stumbled": [
        "['stuhm', 'buhl', 'd']",
        "STMPLT"
    ],
    "stun": [
        "['stuhn']",
        "STN"
    ],
    "stung": [
        "['stuhng']",
        "STNK"
    ],
    "stunk": [
        "['stuhngk']",
        "STNK"
    ],
    "stunned": [
        "[stuhn,ned]",
        "STNT"
    ],
    "stunner": [
        "['stuhn', 'er']",
        "STNR"
    ],
    "stunning": [
        "['stuhn', 'ing']",
        "STNNK"
    ],
    "stunt": [
        "['stuhnt']",
        "STNT"
    ],
    "stunting": [
        "['stuhnt', 'ing']",
        "STNTNK"
    ],
    "stunts": [
        "['stuhnt', 's']",
        "STNTS"
    ],
    "stupid": [
        "['stoo', 'pid']",
        "STPT"
    ],
    "sturdy": [
        "[stur,dee]",
        "STRT"
    ],
    "stutter": [
        "['stuht', 'er']",
        "STTR"
    ],
    "stuttering": [
        "[stuht,er,ing]",
        "STTRNK"
    ],
    "sty": [
        "[stahy]",
        "ST"
    ],
    "style": [
        "['stahyl']",
        "STL"
    ],
    "style's": [
        "[stahyl,'s]",
        "STLS"
    ],
    "styled": [
        "['stahyl', 'd']",
        "STLT"
    ],
    "styles": [
        "['stahyl', 's']",
        "STLS"
    ],
    "stylish": [
        "['stahy', 'lish']",
        "STLX"
    ],
    "stylist": [
        "['stahy', 'list']",
        "STLST"
    ],
    "styrofoam": [
        "['stahy', 'ruh', 'fohm']",
        "STRFM"
    ],
    "styrofoams": [
        "['stahy', 'ruh', 'fohm', 's']",
        "STRFMS"
    ],
    "suave": [
        "[swahv]",
        "SF"
    ],
    "sub": [
        "['suhb']",
        "SP"
    ],
    "subdued": [
        "[suhb,dood]",
        "SPTT"
    ],
    "subject": [
        "['noun']",
        "SPJKT"
    ],
    "sublime": [
        "[suh,blahym]",
        "SPLM"
    ],
    "subliminal": [
        "[suhb,lim,uh,nl]",
        "SPLMNL"
    ],
    "submarine": [
        "['nounsuhb', 'muh', 'reen']",
        "SPMRN"
    ],
    "submission": [
        "[suhb,mish,uhn]",
        "SPMSN"
    ],
    "substance": [
        "['suhb', 'stuhns']",
        "SPSTNS"
    ],
    "substances": [
        "[suhb,stuhns,s]",
        "SPSTNSS"
    ],
    "substitute": [
        "[suhb,sti,toot]",
        "SPSTTT"
    ],
    "subtle": [
        "[suht,l]",
        "SPTL"
    ],
    "subtract": [
        "['suhb', 'trakt']",
        "SPTRKT"
    ],
    "suburban": [
        "['suh', 'bur', 'buhn']",
        "SPRPN"
    ],
    "suburbs": [
        "['suhb', 'urb', 's']",
        "SPRPS"
    ],
    "subway": [
        "['suhb', 'wey']",
        "SP"
    ],
    "succeed": [
        "[suhk,seed]",
        "SKST"
    ],
    "succeeding": [
        "[suhk,see,ding]",
        "SKSTNK"
    ],
    "success": [
        "['suhk', 'ses']",
        "SKSS"
    ],
    "successful": [
        "['suhk', 'ses', 'fuhl']",
        "SKSSFL"
    ],
    "succumb": [
        "[suh,kuhm]",
        "SKMP"
    ],
    "such": [
        "['suhch']",
        "SX"
    ],
    "suck": [
        "['suhk']",
        "SK"
    ],
    "sucked": [
        "['suhk', 'ed']",
        "SKT"
    ],
    "sucker": [
        "['suhk', 'er']",
        "SKR"
    ],
    "suckers": [
        "['suhk', 'er', 's']",
        "SKRS"
    ],
    "sucking": [
        "['suhk', 'ing']",
        "SKNK"
    ],
    "sucks": [
        "['suhk', 's']",
        "SKS"
    ],
    "sudan": [
        "[soo,dan]",
        "STN"
    ],
    "sudden": [
        "['suhd', 'n']",
        "STN"
    ],
    "suddenly": [
        "[suhd,n,ly]",
        "STNL"
    ],
    "sue": [
        "['soo']",
        "S"
    ],
    "sued": [
        "[soo,d]",
        "ST"
    ],
    "suede": [
        "['sweyd']",
        "ST"
    ],
    "suffer": [
        "['suhf', 'er']",
        "SFR"
    ],
    "suffering": [
        "[suhf,er,ing]",
        "SFRNK"
    ],
    "sufficient": [
        "[suh,fish,uhnt]",
        "SFSNT"
    ],
    "suffocate": [
        "['suhf', 'uh', 'keyt']",
        "SFKT"
    ],
    "sugar": [
        "['shoog', 'er']",
        "XKR"
    ],
    "suggest": [
        "['suhg', 'jest']",
        "SKST"
    ],
    "suggested": [
        "[suhg,jest,ed]",
        "SKSTT"
    ],
    "suggestions": [
        "[suhg,jes,chuhn,s]",
        "SKSXNS"
    ],
    "suicidal": [
        "['soo', 'uh', 'sahyd', 'l']",
        "SSTL"
    ],
    "suicide": [
        "['soo', 'uh', 'sahyd']",
        "SST"
    ],
    "suit": [
        "['soot']",
        "ST"
    ],
    "suitcase": [
        "[soot,keys]",
        "STKS"
    ],
    "suite": [
        "['sweetorfor3often']",
        "ST"
    ],
    "suited": [
        "[soo,tid]",
        "STT"
    ],
    "suites": [
        "['sweetorfor3often', 's']",
        "STS"
    ],
    "suits": [
        "['soot', 's']",
        "STS"
    ],
    "sum": [
        "['suhm']",
        "SM"
    ],
    "summer": [
        "['suhm', 'er']",
        "SMR"
    ],
    "summer's": [
        "['suhm', 'er', \"'s\"]",
        "SMRRS"
    ],
    "summers": [
        "['suhm', 'er', 's']",
        "SMRS"
    ],
    "summertime": [
        "['suhm', 'er', 'tahym']",
        "SMRTM"
    ],
    "summing": [
        "[suhm,ming]",
        "SMNK"
    ],
    "sumo": [
        "[soo,moh]",
        "SM"
    ],
    "sun": [
        "['suhn']",
        "SN"
    ],
    "sun's": [
        "['suhn', \"'s\"]",
        "SNNS"
    ],
    "sundae": [
        "['suhn', 'dey']",
        "SNT"
    ],
    "sunday": [
        "['suhn', 'dey']",
        "SNT"
    ],
    "sundays": [
        "[suhn,deyz]",
        "SNTS"
    ],
    "sung": [
        "[suhng]",
        "SNK"
    ],
    "sunk": [
        "[suhngk]",
        "SNK"
    ],
    "sunlight": [
        "['suhn', 'lahyt']",
        "SNLT"
    ],
    "sunny": [
        "['suhn', 'ee']",
        "SN"
    ],
    "sunrise": [
        "['suhn', 'rahyz']",
        "SNRS"
    ],
    "sunroof": [
        "['suhn', 'roof']",
        "SNRF"
    ],
    "suns": [
        "['suhn', 's']",
        "SNS"
    ],
    "sunset": [
        "['suhn', 'set']",
        "SNST"
    ],
    "sunsets": [
        "[suhn,set,s]",
        "SNSTS"
    ],
    "sunshine": [
        "['suhn', 'shahyn']",
        "SNXN"
    ],
    "sup": [
        "[suhp]",
        "SP"
    ],
    "super": [
        "['soo', 'per']",
        "SPR"
    ],
    "superhuman": [
        "[soo,per,hyoo,muhnor]",
        "SPRMN"
    ],
    "superior": [
        "['suh', 'peer', 'ee', 'er']",
        "SPRR"
    ],
    "superman": [
        "['soo', 'per', 'man']",
        "SPRMN"
    ],
    "supermarket": [
        "[soo,per,mahr,kit]",
        "SPRMRKT"
    ],
    "supermodel": [
        "['soo', 'per', 'mod', 'l']",
        "SPRMTL"
    ],
    "supermodels": [
        "['soo', 'per', 'mod', 'l', 's']",
        "SPRMTLS"
    ],
    "supersonic": [
        "[soo,per,son,ik]",
        "SPRSNK"
    ],
    "superstar": [
        "['soo', 'per', 'stahr']",
        "SPRSTR"
    ],
    "superstars": [
        "['soo', 'per', 'stahr', 's']",
        "SPRSTRS"
    ],
    "superstitious": [
        "[soo,per,stish,uhs]",
        "SPRSTTS"
    ],
    "supervised": [
        "[soo,per,vahyz,d]",
        "SPRFST"
    ],
    "supper": [
        "['suhp', 'er']",
        "SPR"
    ],
    "supply": [
        "[suh,plahy]",
        "SPL"
    ],
    "supplying": [
        "['suh', 'plahy', 'ing']",
        "SPLNK"
    ],
    "support": [
        "['suh', 'pawrt']",
        "SPRT"
    ],
    "supported": [
        "[suh,pawrt,ed]",
        "SPRTT"
    ],
    "supporting": [
        "[suh,pawrt,ing]",
        "SPRTNK"
    ],
    "supportive": [
        "[suh,pawr,tiv]",
        "SPRTF"
    ],
    "suppose": [
        "[suh,pohz]",
        "SPS"
    ],
    "supposed": [
        "['suh', 'pohzd']",
        "SPST"
    ],
    "supposedly": [
        "[suh,pohzd,ly]",
        "SPSTL"
    ],
    "supreme": [
        "['suh', 'preem']",
        "SPRM"
    ],
    "sure": [
        "['shoor']",
        "SR"
    ],
    "surely": [
        "['shoor', 'lee']",
        "SRL"
    ],
    "surf": [
        "['surf']",
        "SRF"
    ],
    "surface": [
        "['sur', 'fis']",
        "SRFS"
    ],
    "surfboard": [
        "['surf', 'bawrd']",
        "SRFPRT"
    ],
    "surfing": [
        "['sur', 'fing']",
        "SRFNK"
    ],
    "surgeon": [
        "[sur,juhn]",
        "SRJN"
    ],
    "surgery": [
        "['sur', 'juh', 'ree']",
        "SRKR"
    ],
    "surprise": [
        "['ser', 'prahyz']",
        "SRPRS"
    ],
    "surprised": [
        "['ser', 'prahyz', 'd']",
        "SRPRST"
    ],
    "surprising": [
        "[ser,prahy,zing]",
        "SRPRSNK"
    ],
    "surrender": [
        "['suh', 'ren', 'der']",
        "SRNTR"
    ],
    "surround": [
        "['suh', 'round']",
        "SRNT"
    ],
    "surrounded": [
        "['suh', 'round', 'ed']",
        "SRNTT"
    ],
    "surrounding": [
        "[suh,roun,ding]",
        "SRNTNK"
    ],
    "surveillance": [
        "[ser,vey,luhns]",
        "SRFLNS"
    ],
    "survey": [
        "[verbser,vey]",
        "SRF"
    ],
    "survival": [
        "['ser', 'vahy', 'vuhl']",
        "SRFFL"
    ],
    "survive": [
        "['ser', 'vahyv']",
        "SRFF"
    ],
    "survived": [
        "[ser,vahyv,d]",
        "SRFFT"
    ],
    "survivor": [
        "[ser,vahy,ver]",
        "SRFFR"
    ],
    "survivor's": [
        "[ser,vahy,ver,'s]",
        "SRFFRRS"
    ],
    "sushi": [
        "['soo', 'shee']",
        "SX"
    ],
    "susie": [
        "['soo', 'zee']",
        "SS"
    ],
    "suspect": [
        "['verbsuh', 'spekt']",
        "SSPKT"
    ],
    "suspended": [
        "['suh', 'spend', 'ed']",
        "SSPNTT"
    ],
    "suspenders": [
        "[suh,spen,der,s]",
        "SSPNTRS"
    ],
    "suspension": [
        "[suh,spen,shuhn]",
        "SSPNSN"
    ],
    "suspicious": [
        "['suh', 'spish', 'uhs']",
        "SSPSS"
    ],
    "sutra": [
        "['soo', 'truh']",
        "STR"
    ],
    "swag": [
        "['swag']",
        "SK"
    ],
    "swagged": [
        "['swag', 'ged']",
        "SKT"
    ],
    "swagger": [
        "['swag', 'er']",
        "SKR"
    ],
    "swagger's": [
        "[swag,er,'s]",
        "SKRRS"
    ],
    "swagging": [
        "['swag', 'ging']",
        "SJNK"
    ],
    "swallow": [
        "['swol', 'oh']",
        "SL"
    ],
    "swallowed": [
        "['swol', 'oh', 'ed']",
        "SLT"
    ],
    "swallowing": [
        "['swol', 'oh', 'ing']",
        "SLNK"
    ],
    "swallows": [
        "['swol', 'oh', 's']",
        "SLS"
    ],
    "swam": [
        "['swam']",
        "SM"
    ],
    "swamp": [
        "['swomp']",
        "SMP"
    ],
    "swang": [
        "['swang']",
        "SNK"
    ],
    "swap": [
        "['swop']",
        "SP"
    ],
    "swapped": [
        "[swop,ped]",
        "SPT"
    ],
    "swapping": [
        "['swop', 'ping']",
        "SPNK"
    ],
    "swarm": [
        "[swawrm]",
        "SRM"
    ],
    "swarms": [
        "[swawrm,s]",
        "SRMS"
    ],
    "swat": [
        "[swot]",
        "ST"
    ],
    "swats": [
        "['swats']",
        "STS"
    ],
    "sway": [
        "['swey']",
        "S"
    ],
    "swayed": [
        "[sweyd]",
        "ST"
    ],
    "swear": [
        "['swair']",
        "SR"
    ],
    "swearing": [
        "[swair,ing]",
        "SRNK"
    ],
    "swears": [
        "[swair,s]",
        "SRS"
    ],
    "sweat": [
        "['swet']",
        "ST"
    ],
    "sweater": [
        "['swet', 'er']",
        "STR"
    ],
    "sweaters": [
        "['swet', 'er', 's']",
        "STRS"
    ],
    "sweating": [
        "['swet', 'ing']",
        "STNK"
    ],
    "sweatpants": [
        "[swet,pants]",
        "STPNTS"
    ],
    "sweats": [
        "['swet', 's']",
        "STS"
    ],
    "sweep": [
        "['sweep']",
        "SP"
    ],
    "sweeper": [
        "[swee,per]",
        "SPR"
    ],
    "sweeping": [
        "[swee,ping]",
        "SPNK"
    ],
    "sweet": [
        "['sweet']",
        "ST"
    ],
    "sweeter": [
        "['sweet', 'er']",
        "STR"
    ],
    "sweetest": [
        "['sweet', 'est']",
        "STST"
    ],
    "sweetheart": [
        "[sweet,hahrt]",
        "S0RT"
    ],
    "sweethearts": [
        "[sweet,hahrt,s]",
        "S0RTS"
    ],
    "sweetie": [
        "[swee,tee]",
        "ST"
    ],
    "sweets": [
        "['sweet', 's']",
        "STS"
    ],
    "swell": [
        "[swel]",
        "SL"
    ],
    "swept": [
        "[swept]",
        "SPT"
    ],
    "swerve": [
        "['swurv']",
        "SRF"
    ],
    "swerved": [
        "['swurv', 'd']",
        "SRFT"
    ],
    "swerves": [
        "[swurv,s]",
        "SRFS"
    ],
    "swift": [
        "[swift]",
        "SFT"
    ],
    "swiftly": [
        "[swift,ly]",
        "SFTL"
    ],
    "swim": [
        "['swim']",
        "SM"
    ],
    "swimmers": [
        "['swim', 'mers']",
        "SMRS"
    ],
    "swimming": [
        "['swim', 'ing']",
        "SMNK"
    ],
    "swimwear": [
        "['swim', 'wair']",
        "SMR"
    ],
    "swine": [
        "['swahyn']",
        "SN"
    ],
    "swing": [
        "['swing']",
        "SNK"
    ],
    "swingers": [
        "[swing,er,s]",
        "SNKRS"
    ],
    "swinging": [
        "['swing', 'ing']",
        "SNJNK"
    ],
    "swings": [
        "['swing', 's']",
        "SNKS"
    ],
    "swipe": [
        "['swahyp']",
        "SP"
    ],
    "swish": [
        "['swish']",
        "SX"
    ],
    "swisher": [
        "[swish,er]",
        "SXR"
    ],
    "swishers": [
        "['swish', 'ers']",
        "SXRS"
    ],
    "swishes": [
        "['swish', 'es']",
        "SXS"
    ],
    "swiss": [
        "['swis']",
        "SS"
    ],
    "switch": [
        "['swich']",
        "SX"
    ],
    "switched": [
        "['swich', 'ed']",
        "SXT"
    ],
    "switcheroo": [
        "['swich', 'uh', 'roo']",
        "SXR"
    ],
    "switches": [
        "['swich', 'es']",
        "SXS"
    ],
    "switching": [
        "['swich', 'ing']",
        "SXNK"
    ],
    "switzerland": [
        "[swit,ser,luhnd]",
        "STSRLNT"
    ],
    "swivel": [
        "[swiv,uhl]",
        "SFL"
    ],
    "swole": [
        [
            "swoh",
            "luh"
        ],
        "SL"
    ],
    "swollen": [
        "['swoh', 'luhn']",
        "SLN"
    ],
    "swoop": [
        "['swoop']",
        "SP"
    ],
    "swooped": [
        "[swoop,ed]",
        "SPT"
    ],
    "swoosh": [
        "['swoosh']",
        "SX"
    ],
    "sword": [
        "['sawrd']",
        "SRT"
    ],
    "swordfish": [
        "['sawrd', 'fish']",
        "SRTFX"
    ],
    "swords": [
        "[sawrd,s]",
        "SRTS"
    ],
    "swore": [
        "[swawr]",
        "SR"
    ],
    "sworn": [
        "['swawrn']",
        "SRN"
    ],
    "swung": [
        "[swuhng]",
        "SNK"
    ],
    "sydney": [
        "[sid,nee]",
        "STN"
    ],
    "syllable": [
        "[sil,uh,buhl]",
        "SLPL"
    ],
    "syllables": [
        "[sil,uh,buhl,s]",
        "SLPLS"
    ],
    "symbol": [
        "['sim', 'buhl']",
        "SMPL"
    ],
    "symbolic": [
        "[sim,bol,ik]",
        "SMPLK"
    ],
    "symbolism": [
        "[sim,buh,liz,uhm]",
        "SMPLSM"
    ],
    "sympathy": [
        "['sim', 'puh', 'thee']",
        "SMP0"
    ],
    "symphony": [
        "[sim,fuh,nee]",
        "SMFN"
    ],
    "symptoms": [
        "['simp', 'tuhm', 's']",
        "SMPTMS"
    ],
    "synagogue": [
        "[sin,uh,gog]",
        "SNKK"
    ],
    "sync": [
        "['singk']",
        "SNK"
    ],
    "syndrome": [
        "[sin,drohm]",
        "SNTRM"
    ],
    "synonym": [
        "[sin,uh,nim]",
        "SNNM"
    ],
    "synonyms": [
        "[sin,uh,nim,s]",
        "SNNMS"
    ],
    "synopsis": [
        "[si,nop,sis]",
        "SNPSS"
    ],
    "syntax": [
        "[sin,taks]",
        "SNTKS"
    ],
    "synthetic": [
        "['sin', 'thet', 'ik']",
        "SN0TK"
    ],
    "syringes": [
        "['suh', 'rinj', 's']",
        "SRNJS"
    ],
    "syrup": [
        "['sir', 'uhp']",
        "SRP"
    ],
    "system": [
        "['sis', 'tuhm']",
        "SSTM"
    ],
    "system's": [
        "[sis,tuhm,'s]",
        "SSTMMS"
    ],
    "t": [
        "['tee', '']",
        "T"
    ],
    "ta": [
        "['tah']",
        "T"
    ],
    "tab": [
        "['tab']",
        "TP"
    ],
    "tabernacle": [
        "['tab', 'er', 'nak', 'uhl']",
        "TPRNKL"
    ],
    "table": [
        "['tey', 'buhl']",
        "TPL"
    ],
    "tables": [
        "['tey', 'buhl', 's']",
        "TPLS"
    ],
    "tablet": [
        "['tab', 'lit']",
        "TPLT"
    ],
    "tabs": [
        "['tab', 's']",
        "TPS"
    ],
    "tack": [
        "[tak]",
        "TK"
    ],
    "tackle": [
        "[tak,uhlorfor24]",
        "TKL"
    ],
    "tacky": [
        "[tak,ee]",
        "TK"
    ],
    "taco": [
        "['tah', 'koh']",
        "TK"
    ],
    "tacos": [
        "['tah', 'koh', 's']",
        "TKS"
    ],
    "tact": [
        "[takt]",
        "TKT"
    ],
    "tactician": [
        "[tak,tish,uhn]",
        "TKTSN"
    ],
    "tactics": [
        "['tak', 'tiks']",
        "TKTKS"
    ],
    "tad": [
        "[tad]",
        "TT"
    ],
    "tag": [
        "['tag']",
        "TK"
    ],
    "tagged": [
        "['tag', 'ged']",
        "TKT"
    ],
    "tagging": [
        "[tag,ging]",
        "TJNK"
    ],
    "tags": [
        "['tag', 's']",
        "TKS"
    ],
    "tahiti": [
        "[tuh,hee,tee]",
        "THT"
    ],
    "tai": [
        "[tahy]",
        "T"
    ],
    "tail": [
        "['teyl']",
        "TL"
    ],
    "tailor": [
        "[tey,ler]",
        "TLR"
    ],
    "tailored": [
        "['tey', 'lerd']",
        "TLRT"
    ],
    "tails": [
        "['teylz']",
        "TLS"
    ],
    "taint": [
        "[teynt]",
        "TNT"
    ],
    "tainted": [
        "['teynt', 'ed']",
        "TNTT"
    ],
    "take": [
        "['teyk']",
        "TK"
    ],
    "taken": [
        "['tey', 'kuhn']",
        "TKN"
    ],
    "takeoff": [
        "['teyk', 'awf']",
        "TKF"
    ],
    "takeover": [
        "['teyk', 'oh', 'ver']",
        "TKFR"
    ],
    "taker": [
        "[teyk,r]",
        "TKR"
    ],
    "takers": [
        "['teyk', 'rs']",
        "TKRS"
    ],
    "takes": [
        "['teyk', 's']",
        "TKS"
    ],
    "taki": [
        [
            "tah",
            "kee"
        ],
        "TK"
    ],
    "taking": [
        "['tey', 'king']",
        "TKNK"
    ],
    "tale": [
        "['teyl']",
        "TL"
    ],
    "talent": [
        "['tal', 'uhnt']",
        "TLNT"
    ],
    "talented": [
        "['tal', 'uhn', 'tid']",
        "TLNTT"
    ],
    "talents": [
        "[tal,uhnt,s]",
        "TLNTS"
    ],
    "tales": [
        "['teylz']",
        "TLS"
    ],
    "taliban": [
        "['tal', 'uh', 'ban']",
        "TLPN"
    ],
    "talk": [
        "['tawk']",
        "TLK"
    ],
    "talked": [
        "['tawk', 'ed']",
        "TLKT"
    ],
    "talker": [
        "['tawk', 'er']",
        "TLKR"
    ],
    "talkie": [
        "['taw', 'kee']",
        "TLK"
    ],
    "talking": [
        "['tawk', 'ing']",
        "TLKNK"
    ],
    "talks": [
        "['tawk', 's']",
        "TLKS"
    ],
    "tall": [
        "['tawl']",
        "TL"
    ],
    "tallahassee": [
        "[tal,uh,has,ee]",
        "TLHS"
    ],
    "taller": [
        "['tawl', 'er']",
        "TLR"
    ],
    "tamale": [
        "[tuh,mah,lee]",
        "TML"
    ],
    "tambourine": [
        "['tam', 'buh', 'reen']",
        "TMPRN"
    ],
    "tame": [
        "['teym']",
        "TM"
    ],
    "tamed": [
        "['teym', 'd']",
        "TMT"
    ],
    "tammy": [
        "['tam', 'ee']",
        "TM"
    ],
    "tampa": [
        "[tam,puh]",
        "TMP"
    ],
    "tampon": [
        "['tam', 'pon']",
        "TMPN"
    ],
    "tan": [
        "['tan']",
        "TN"
    ],
    "tandem": [
        "[tan,duhm]",
        "TNTM"
    ],
    "tang": [
        "['tang']",
        "TNK"
    ],
    "tangerine": [
        "['tan', 'juh', 'reen']",
        "TNKRN"
    ],
    "tangle": [
        "[tang,guhl]",
        "TNKL"
    ],
    "tangled": [
        "[tang,guhld]",
        "TNKLT"
    ],
    "tango": [
        "['tang', 'goh']",
        "TNK"
    ],
    "tank": [
        "['tangk']",
        "TNK"
    ],
    "tanks": [
        "[tangk,s]",
        "TNKS"
    ],
    "tanned": [
        "['tan', 'ned']",
        "TNT"
    ],
    "tanning": [
        "['tan', 'ing']",
        "TNNK"
    ],
    "tantrum": [
        "['tan', 'truhm']",
        "TNTRM"
    ],
    "tantrums": [
        "['tan', 'truhm', 's']",
        "TNTRMS"
    ],
    "tap": [
        "['tap']",
        "TP"
    ],
    "tape": [
        "['teyp']",
        "TP"
    ],
    "taped": [
        "['teyp', 'd']",
        "TPT"
    ],
    "tapes": [
        "[teyp,s]",
        "TPS"
    ],
    "tapped": [
        "['tap', 'ped']",
        "TPT"
    ],
    "tapping": [
        "[tap,ing]",
        "TPNK"
    ],
    "taps": [
        "[taps]",
        "TPS"
    ],
    "tar": [
        "['tahr']",
        "TR"
    ],
    "tarantula": [
        "['tuh', 'ran', 'chuh', 'luh']",
        "TRNTL"
    ],
    "target": [
        "['tahr', 'git']",
        "TRKT"
    ],
    "targeted": [
        "['tahr', 'git', 'ed']",
        "TRKTT"
    ],
    "targets": [
        "['tahr', 'git', 's']",
        "TRKTS"
    ],
    "tart": [
        "['tahrt']",
        "TRT"
    ],
    "tarts": [
        "[tahrt,s]",
        "TRTS"
    ],
    "tarzan": [
        "[tahr,zuhn]",
        "TRSN"
    ],
    "task": [
        "['task']",
        "TSK"
    ],
    "taste": [
        "['teyst']",
        "TST"
    ],
    "tastes": [
        "['teyst', 's']",
        "TSTS"
    ],
    "tasty": [
        "[tey,stee]",
        "TST"
    ],
    "tat": [
        "['tat']",
        "TT"
    ],
    "tater": [
        "['tey', 'ter']",
        "TTR"
    ],
    "tats": [
        "['tat', 's']",
        "TTS"
    ],
    "tatted": [
        "['tat', 'ted']",
        "TTT"
    ],
    "tattle": [
        "['tat', 'l']",
        "TTL"
    ],
    "tattoo": [
        "['ta', 'too']",
        "TT"
    ],
    "tattooed": [
        "['ta', 'too', 'ed']",
        "TTT"
    ],
    "tattoos": [
        "['ta', 'too', 's']",
        "TTS"
    ],
    "taught": [
        "['tawt']",
        "TFT"
    ],
    "tax": [
        "['taks']",
        "TKS"
    ],
    "taxes": [
        "['taks', 'es']",
        "TKSS"
    ],
    "taxi": [
        "['tak', 'see']",
        "TKS"
    ],
    "taxing": [
        "[tak,sing]",
        "TKSNK"
    ],
    "tay": [
        "['tey']",
        "T"
    ],
    "taylor": [
        "[tey,ler]",
        "TLR"
    ],
    "taylors": [
        "[tey,ler,s]",
        "TLRS"
    ],
    "te": [
        "['tey']",
        "T"
    ],
    "tea": [
        "['tee']",
        "T"
    ],
    "teach": [
        "['teech']",
        "TX"
    ],
    "teacher": [
        "['tee', 'cher']",
        "TXR"
    ],
    "teacher's": [
        "['tee', 'cher', \"'s\"]",
        "TXRRS"
    ],
    "teachers": [
        "['tee', 'cher', 's']",
        "TXRS"
    ],
    "teaching": [
        "['tee', 'ching']",
        "TXNK"
    ],
    "team": [
        "['teem']",
        "TM"
    ],
    "team's": [
        "[teem,'s]",
        "TMMS"
    ],
    "teams": [
        "['teem', 's']",
        "TMS"
    ],
    "tear": [
        "['teer']",
        "TR"
    ],
    "teardrops": [
        "['teer', 'drop', 's']",
        "TRTRPS"
    ],
    "tearing": [
        "['teer', 'ing']",
        "TRNK"
    ],
    "tears": [
        "['teer', 's']",
        "TRS"
    ],
    "tease": [
        "['teez']",
        "TS"
    ],
    "teased": [
        "[teez,d]",
        "TST"
    ],
    "teaser": [
        "['tee', 'zer']",
        "TSR"
    ],
    "tec": [
        "['tek']",
        "TK"
    ],
    "tech": [
        "['tek']",
        "TX"
    ],
    "technical": [
        "['tek', 'ni', 'kuhl']",
        "TKNKL"
    ],
    "technically": [
        "['tek', 'ni', 'kuhl', 'ly']",
        "TKNKL"
    ],
    "technique": [
        "[tek,neek]",
        "TKNK"
    ],
    "technology": [
        "[tek,nol,uh,jee]",
        "TKNLJ"
    ],
    "techs": [
        "[tek,s]",
        "TKS"
    ],
    "tecs": [
        "[tek,s]",
        "TKS"
    ],
    "ted": [
        "[ted]",
        "TT"
    ],
    "teddy": [
        "['ted', 'ee']",
        "TT"
    ],
    "tee": [
        "['tee']",
        "T"
    ],
    "teen": [
        "['teen']",
        "TN"
    ],
    "teenage": [
        "[teen,eyj]",
        "TNJ"
    ],
    "teenager": [
        "['teen', 'ey', 'jer']",
        "TNKR"
    ],
    "teenagers": [
        "[teen,ey,jer,s]",
        "TNKRS"
    ],
    "teens": [
        "['teenz']",
        "TNS"
    ],
    "teeny": [
        "['tee', 'nee']",
        "TN"
    ],
    "teepee": [
        "[tee,pee]",
        "TP"
    ],
    "tees": [
        "['teez']",
        "TS"
    ],
    "teeth": [
        "['teeth']",
        "T0"
    ],
    "teething": [
        "['tee', 'thing']",
        "T0NK"
    ],
    "telephone": [
        "['tel', 'uh', 'fohn']",
        "TLFN"
    ],
    "televised": [
        "['tel', 'uh', 'vahyz', 'd']",
        "TLFST"
    ],
    "television": [
        "[tel,uh,vizh,uhn]",
        "TLFSN"
    ],
    "tell": [
        "['tel']",
        "TL"
    ],
    "teller": [
        "['tel', 'er']",
        "TLR"
    ],
    "telling": [
        "['tel', 'ing']",
        "TLNK"
    ],
    "tells": [
        "['tel', 's']",
        "TLS"
    ],
    "telly": [
        "['tel', 'ee']",
        "TL"
    ],
    "temp": [
        "['temp']",
        "TMP"
    ],
    "temper": [
        "[tem,per]",
        "TMPR"
    ],
    "temperature": [
        "['tem', 'per', 'uh', 'cher']",
        "TMPRTR"
    ],
    "tempers": [
        "[tem,per,s]",
        "TMPRS"
    ],
    "temple": [
        "['tem', 'puhl']",
        "TMPL"
    ],
    "tempo": [
        "['tem', 'poh']",
        "TMP"
    ],
    "temporary": [
        "['tem', 'puh', 'rer', 'ee']",
        "TMPRR"
    ],
    "tempt": [
        "[tempt]",
        "TMPT"
    ],
    "temptation": [
        "[temp,tey,shuhn]",
        "TMPTXN"
    ],
    "temptations": [
        "['temp', 'tey', 'shuhn', 's']",
        "TMPTXNS"
    ],
    "tempted": [
        "[tempt,ed]",
        "TMPTT"
    ],
    "ten": [
        "['ten']",
        "TN"
    ],
    "tenacity": [
        "[tuh,nas,i,tee]",
        "TNST"
    ],
    "tenant": [
        "['ten', 'uhnt']",
        "TNNT"
    ],
    "tenants": [
        "[ten,uhnt,s]",
        "TNNTS"
    ],
    "tend": [
        "[tend]",
        "TNT"
    ],
    "tender": [
        "[ten,der]",
        "TNTR"
    ],
    "tenderness": [
        "[ten,der,ness]",
        "TNTRNS"
    ],
    "tenement": [
        "[ten,uh,muhnt]",
        "TNMNT"
    ],
    "tennessee": [
        "['ten', 'uh', 'see']",
        "TNS"
    ],
    "tennis": [
        "['ten', 'is']",
        "TNS"
    ],
    "tens": [
        "['tenz']",
        "TNS"
    ],
    "tense": [
        "['tens']",
        "TNS"
    ],
    "tension": [
        "['ten', 'shuhn']",
        "TNSN"
    ],
    "tent": [
        "['tent']",
        "TNT"
    ],
    "tenth": [
        "[tenth]",
        "TN0"
    ],
    "tequila": [
        "[tuh,kee,luh]",
        "TKL"
    ],
    "teriyaki": [
        "['ter', 'uh', 'yah', 'kee']",
        "TRK"
    ],
    "term": [
        "['turm']",
        "TRM"
    ],
    "terminate": [
        "['tur', 'muh', 'neyt']",
        "TRMNT"
    ],
    "terminator": [
        "['tur', 'muh', 'ney', 'ter']",
        "TRMNTR"
    ],
    "terms": [
        "[turm,s]",
        "TRMS"
    ],
    "terrapins": [
        "[ter,uh,pin,s]",
        "TRPNS"
    ],
    "terrible": [
        "[ter,uh,buhl]",
        "TRPL"
    ],
    "terrific": [
        "['tuh', 'rif', 'ik']",
        "TRFK"
    ],
    "territory": [
        "['ter', 'i', 'tawr', 'ee']",
        "TRTR"
    ],
    "terror": [
        "[ter,er]",
        "TRR"
    ],
    "terrorist": [
        "['ter', 'er', 'ist']",
        "TRRST"
    ],
    "terry": [
        "[ter,ee]",
        "TR"
    ],
    "tes": [
        "[tey,s]",
        "TS"
    ],
    "tesla": [
        "['tes', 'luh']",
        "TSL"
    ],
    "test": [
        "['test']",
        "TST"
    ],
    "testament": [
        "[tes,tuh,muhnt]",
        "TSTMNT"
    ],
    "tested": [
        "[test,ed]",
        "TSTT"
    ],
    "testify": [
        "['tes', 'tuh', 'fahy']",
        "TSTF"
    ],
    "testimony": [
        "['tes', 'tuh', 'moh', 'nee']",
        "TSTMN"
    ],
    "testing": [
        "['test', 'ing']",
        "TSTNK"
    ],
    "texas": [
        "['tek', 'suhs']",
        "TKSS"
    ],
    "text": [
        "['tekst']",
        "TKST"
    ],
    "texting": [
        "['tekst', 'ing']",
        "TKSTNK"
    ],
    "texts": [
        "['tekst', 's']",
        "TKSTS"
    ],
    "th": [
        "['thr', 'm']",
        "0"
    ],
    "thailand": [
        "[tahy,land]",
        "0LNT"
    ],
    "than": [
        "['than']",
        "0N"
    ],
    "thank": [
        "['thangk']",
        "0NK"
    ],
    "thanked": [
        "['thangk', 'ed']",
        "0NKT"
    ],
    "thankful": [
        "[thangk,fuhl]",
        "0NKFL"
    ],
    "thanking": [
        "['thangk', 'ing']",
        "0NKNK"
    ],
    "thanks": [
        "['thangk', 's']",
        "0NKS"
    ],
    "thanksgiving": [
        "['thangks', 'giv', 'ing']",
        "0NKSJFNK"
    ],
    "that": [
        "['that']",
        "0T"
    ],
    "that's": [
        "['thats']",
        "0TTS"
    ],
    "thawed": [
        "[thaw,ed]",
        "0T"
    ],
    "thc": [
        "[(tch,s)]",
        "0K"
    ],
    "the": [
        "['stressedthee']",
        "0"
    ],
    "theater": [
        "[thee,uh,ter]",
        "0TR"
    ],
    "theft": [
        "[theft]",
        "0FT"
    ],
    "their": [
        "['thair']",
        "0R"
    ],
    "theirs": [
        "['thairz']",
        "0RS"
    ],
    "them": [
        "['them']",
        "0M"
    ],
    "theme": [
        "['theem']",
        "0M"
    ],
    "themselves": [
        "['thuhm', 'selvz']",
        "0MSLFS"
    ],
    "then": [
        "['then']",
        "0N"
    ],
    "theory": [
        "[thee,uh,ree]",
        "0R"
    ],
    "therapist": [
        "[ther,uh,pist]",
        "0RPST"
    ],
    "therapy": [
        "['ther', 'uh', 'pee']",
        "0RP"
    ],
    "there": [
        "['thair']",
        "0R"
    ],
    "there's": [
        "['thairz']",
        "0RS"
    ],
    "therefore": [
        "['thair', 'fawr']",
        "0RFR"
    ],
    "theres": [
        "['thair', 's']",
        "0RS"
    ],
    "thermal": [
        "[thur,muhl]",
        "0RML"
    ],
    "thermometer": [
        "[ther,mom,i,ter]",
        "0RMMTR"
    ],
    "these": [
        "['theez']",
        "0S"
    ],
    "thespian": [
        "[thes,pee,uhn]",
        "0SPN"
    ],
    "they": [
        "['they']",
        "0"
    ],
    "they'd": [
        "['theyd']",
        "0T"
    ],
    "they'll": [
        "['theyl']",
        "0L"
    ],
    "they're": [
        "['thair']",
        "0R"
    ],
    "they've": [
        "['theyv']",
        "0F"
    ],
    "thick": [
        "['thik']",
        "0K"
    ],
    "thicker": [
        "['thik', 'er']",
        "0KR"
    ],
    "thief": [
        "['theef']",
        "0F"
    ],
    "thigh": [
        "['thahy']",
        "0"
    ],
    "thighs": [
        "['thahy', 's']",
        "0S"
    ],
    "thin": [
        "['thin']",
        "0N"
    ],
    "thing": [
        "['thing']",
        "0NK"
    ],
    "thing's": [
        "[thing,'s]",
        "0NKKS"
    ],
    "things": [
        "['thing', 's']",
        "0NKS"
    ],
    "think": [
        "['thingk']",
        "0NK"
    ],
    "thinker": [
        "[thing,ker]",
        "0NKR"
    ],
    "thinking": [
        "['thing', 'king']",
        "0NKNK"
    ],
    "thinks": [
        "[thingk,s]",
        "0NKS"
    ],
    "thinner": [
        "[thin,er]",
        "0NR"
    ],
    "thinnest": [
        "['thin', 'nest']",
        "0NST"
    ],
    "thinning": [
        "[thin,ning]",
        "0NNK"
    ],
    "third": [
        "['thurd']",
        "0RT"
    ],
    "thirst": [
        "[thurst]",
        "0RST"
    ],
    "thirsty": [
        "['thur', 'stee']",
        "0RST"
    ],
    "thirteen": [
        "['thur', 'teen']",
        "0RTN"
    ],
    "thirty": [
        "['thur', 'tee']",
        "0RT"
    ],
    "this": [
        "['this']",
        "0S"
    ],
    "tho": [
        "['thoh']",
        "0"
    ],
    "thomas": [
        "[tom,uhstaw]",
        "TMS"
    ],
    "thong": [
        "['thawng']",
        "0NK"
    ],
    "thongs": [
        "[thawng,s]",
        "0NKS"
    ],
    "thorough": [
        "['thur', 'oh']",
        "0RF"
    ],
    "thoroughbred": [
        "['thur', 'oh', 'bred']",
        "0RFPRT"
    ],
    "those": [
        "['thohz']",
        "0S"
    ],
    "thot": [
        "['thotorthot', 'ee']",
        "0T"
    ],
    "thots": [
        "['thotorthot', 'ee', 's']",
        "0TS"
    ],
    "thottie": [
        "['thotorthot', 'ee', 'tie']",
        "0T"
    ],
    "thotties": [
        "['thotorthot', 'ee', 'ties']",
        "0TS"
    ],
    "thotty": [
        [
            "thawt",
            "ee"
        ],
        "0T"
    ],
    "thou": [
        "['thou']",
        "0"
    ],
    "though": [
        "['thoh']",
        "0"
    ],
    "thought": [
        "['thawt']",
        "0T"
    ],
    "thoughts": [
        "['thawt', 's']",
        "0TS"
    ],
    "thousand": [
        "['thou', 'zuhnd']",
        "0SNT"
    ],
    "thousands": [
        "['thou', 'zuhnd', 's']",
        "0SNTS"
    ],
    "thrash": [
        "['thrash']",
        "0RX"
    ],
    "thrashing": [
        "[thrash,ing]",
        "0RXNK"
    ],
    "thrax": [
        [
            "thr",
            "aks"
        ],
        "0RKS"
    ],
    "thread": [
        "[thred]",
        "0RT"
    ],
    "threads": [
        "[thred,s]",
        "0RTS"
    ],
    "threat": [
        "['thret']",
        "0RT"
    ],
    "threaten": [
        "[thret,n]",
        "0RTN"
    ],
    "threatened": [
        "[thret,n,ed]",
        "0RTNT"
    ],
    "threatening": [
        "[thret,n,ing]",
        "0RTNNK"
    ],
    "threats": [
        "['thret', 's']",
        "0RTS"
    ],
    "three": [
        "['three']",
        "0R"
    ],
    "three's": [
        "[three,'s]",
        "0RS"
    ],
    "threes": [
        "[three,s]",
        "0RS"
    ],
    "threesome": [
        "['three', 'suhm']",
        "0RSM"
    ],
    "threesomes": [
        "[three,suhm,s]",
        "0RSMS"
    ],
    "threw": [
        "['throo']",
        "0R"
    ],
    "thrift": [
        "['thrift']",
        "0RFT"
    ],
    "thrill": [
        "['thril']",
        "0RL"
    ],
    "thriller": [
        "['thril', 'er']",
        "0RLR"
    ],
    "throat": [
        "['throht']",
        "0RT"
    ],
    "throats": [
        "[throht,s]",
        "0RTS"
    ],
    "throne": [
        "['throhn']",
        "0RN"
    ],
    "throttle": [
        "['throt', 'l']",
        "0RTL"
    ],
    "through": [
        "['throo']",
        "0R"
    ],
    "throughout": [
        "[throo,out]",
        "0RT"
    ],
    "throw": [
        "['throh']",
        "0R"
    ],
    "throwaway": [
        "['throh', 'uh', 'wey']",
        "0R"
    ],
    "throwback": [
        "[throh,bak]",
        "0RPK"
    ],
    "throwed": [
        "['throhd']",
        "0RT"
    ],
    "thrower": [
        "['throh', 'er']",
        "0RR"
    ],
    "throwing": [
        "['throh', 'ing']",
        "0RNK"
    ],
    "thrown": [
        "['throhn']",
        "0RN"
    ],
    "throws": [
        "['throh', 's']",
        "0RS"
    ],
    "thrust": [
        "[thruhst]",
        "0RST"
    ],
    "thug": [
        "['thuhg']",
        "0K"
    ],
    "thug's": [
        "[thuhg,'s]",
        "0KKS"
    ],
    "thugging": [
        [
            "thuhg",
            "ing"
        ],
        "0KNK"
    ],
    "thugs": [
        "['thuhg', 's']",
        "0KS"
    ],
    "thumb": [
        "['thuhm']",
        "0MP"
    ],
    "thumbing": [
        "['thuhm', 'ing']",
        "0MPNK"
    ],
    "thumbs": [
        "[thuhm,s]",
        "0MPS"
    ],
    "thump": [
        "['thuhmp']",
        "0MP"
    ],
    "thumping": [
        "['thuhm', 'ping']",
        "0MPNK"
    ],
    "thunder": [
        "['thuhn', 'der']",
        "0NTR"
    ],
    "thunderous": [
        "[thuhn,der,uhs]",
        "0NTRS"
    ],
    "thunderstorm": [
        "['thuhn', 'der', 'stawrm']",
        "0NTRSTRM"
    ],
    "thursday": [
        "['thurz', 'dey']",
        "0RST"
    ],
    "thursdays": [
        "[thurz,deyz]",
        "0RSTS"
    ],
    "thus": [
        "[thuhs]",
        "0S"
    ],
    "ti": [
        "[tee]",
        "T"
    ],
    "tic": [
        "['tik']",
        "TK"
    ],
    "tick": [
        "['tik']",
        "TK"
    ],
    "ticket": [
        "['tik', 'it']",
        "TKT"
    ],
    "tickets": [
        "['tik', 'it', 's']",
        "TKTS"
    ],
    "ticking": [
        "['tik', 'ing']",
        "TKNK"
    ],
    "tickle": [
        "['tik', 'uhl']",
        "TKL"
    ],
    "tickles": [
        "[tik,uhl,s]",
        "TKLS"
    ],
    "ticklish": [
        "[tik,lish]",
        "TKLX"
    ],
    "ticks": [
        "['tik', 's']",
        "TKS"
    ],
    "tics": [
        "[tik,s]",
        "TKS"
    ],
    "tidal": [
        "['tahyd', 'l']",
        "TTL"
    ],
    "tide": [
        "[tahyd]",
        "TT"
    ],
    "tides": [
        "[tahyd,s]",
        "TTS"
    ],
    "tie": [
        "['tahy']",
        "T"
    ],
    "tied": [
        "['tahy', 'd']",
        "TT"
    ],
    "tier": [
        "[teer]",
        "T"
    ],
    "ties": [
        "['tahy', 's']",
        "TS"
    ],
    "tiffany": [
        "['tif', 'uh', 'nee']",
        "TFN"
    ],
    "tiffany's": [
        "['tif', 'uh', 'nee', \"'s\"]",
        "TFNS"
    ],
    "tiger": [
        "['tahy', 'ger']",
        "TJR"
    ],
    "tigers": [
        "['tahy', 'ger', 's']",
        "TJRS"
    ],
    "tight": [
        "['tahyt']",
        "TT"
    ],
    "tighter": [
        "['tahyt', 'er']",
        "TTR"
    ],
    "tightest": [
        "[tahyt,est]",
        "TTST"
    ],
    "tightly": [
        "[tahyt,ly]",
        "TTL"
    ],
    "tights": [
        "['tahyts']",
        "TTS"
    ],
    "tijuana": [
        "['tee', 'uh', 'wah', 'nuh']",
        "TJN"
    ],
    "till": [
        "['til']",
        "TL"
    ],
    "tilt": [
        "['tilt']",
        "TLT"
    ],
    "timber": [
        "['tim', 'ber']",
        "TMPR"
    ],
    "timberland": [
        "['tim', 'ber', 'land']",
        "TMPRLNT"
    ],
    "timberlands": [
        "['tim', 'ber', 'land', 's']",
        "TMPRLNTS"
    ],
    "timbs": [
        [
            "tim",
            "bee"
        ],
        "TMPS"
    ],
    "time": [
        "['tahym']",
        "TM"
    ],
    "time's": [
        "['tahym', \"'s\"]",
        "TMS"
    ],
    "timeless": [
        "['tahym', 'lis']",
        "TMLS"
    ],
    "timeline": [
        "[tahym,lahyn]",
        "TMLN"
    ],
    "timepiece": [
        "[tahym,pees]",
        "TMPS"
    ],
    "timer": [
        "[tahy,mer]",
        "TMR"
    ],
    "times": [
        "['tahymz']",
        "TMS"
    ],
    "timid": [
        "[tim,id]",
        "TMT"
    ],
    "timing": [
        "['tahy', 'ming']",
        "TMNK"
    ],
    "tina": [
        "['tee', 'nuh']",
        "TN"
    ],
    "tinder": [
        "['tin', 'der']",
        "TNTR"
    ],
    "ting": [
        "['ting']",
        "TNK"
    ],
    "tingle": [
        "[ting,guhl]",
        "TNKL"
    ],
    "tings": [
        "[ting,s]",
        "TNKS"
    ],
    "tint": [
        "['tint']",
        "TNT"
    ],
    "tinted": [
        "['tint', 'ed']",
        "TNTT"
    ],
    "tints": [
        "['tint', 's']",
        "TNTS"
    ],
    "tiny": [
        "['tahy', 'nee']",
        "TN"
    ],
    "tip": [
        "['tip']",
        "TP"
    ],
    "tipped": [
        "[tip,ped]",
        "TPT"
    ],
    "tipper": [
        "[tip,er]",
        "TPR"
    ],
    "tipping": [
        "['tip', 'ping']",
        "TPNK"
    ],
    "tippy": [
        "[tip,ee]",
        "TP"
    ],
    "tips": [
        "['tip', 's']",
        "TPS"
    ],
    "tipsy": [
        "['tip', 'see']",
        "TPS"
    ],
    "tire": [
        "['tahyuhr']",
        "TR"
    ],
    "tired": [
        "['tahyuhrd']",
        "TRT"
    ],
    "tires": [
        "['tahyuhr', 's']",
        "TRS"
    ],
    "tis": [
        "[tee,s]",
        "TS"
    ],
    "tissue": [
        "['tish', 'ooor']",
        "TS"
    ],
    "tissues": [
        "[tish,ooor,s]",
        "TSS"
    ],
    "tit": [
        "['tit']",
        "TT"
    ],
    "titanic": [
        "['tahy', 'tan', 'ik']",
        "TTNK"
    ],
    "titans": [
        "['tahyt', 'n', 's']",
        "TTNS"
    ],
    "tithes": [
        "[tahyth,s]",
        "T0S"
    ],
    "title": [
        "['tahyt', 'l']",
        "TTL"
    ],
    "titles": [
        "[tahyt,l,s]",
        "TTLS"
    ],
    "tito": [
        "['tee', 'toh']",
        "TT"
    ],
    "tits": [
        "['tit', 's']",
        "TTS"
    ],
    "titties": [
        "['tit', 'ee', 's']",
        "TTS"
    ],
    "titty": [
        "['tit', 'ee']",
        "TT"
    ],
    "tnt": [
        "['tn', 't']",
        "TNT"
    ],
    "to": [
        "['too']",
        "T"
    ],
    "toast": [
        "['tohst']",
        "TST"
    ],
    "toasted": [
        "['tohst', 'ed']",
        "TSTT"
    ],
    "toaster": [
        "['toh', 'ster']",
        "TSTR"
    ],
    "toasters": [
        "[toh,ster,s]",
        "TSTRS"
    ],
    "toasting": [
        "[tohst,ing]",
        "TSTNK"
    ],
    "toasts": [
        "['tohst', 's']",
        "TSTS"
    ],
    "tobacco": [
        "['tuh', 'bak', 'oh']",
        "TPK"
    ],
    "today": [
        "['tuh', 'dey']",
        "TT"
    ],
    "today's": [
        "['tuh', 'dey', \"'s\"]",
        "TTS"
    ],
    "todd": [
        "[tod]",
        "TT"
    ],
    "toddler": [
        "[tod,ler]",
        "TTLR"
    ],
    "toe": [
        "['toh']",
        "T"
    ],
    "toed": [
        "[tohd]",
        "TT"
    ],
    "toeing": [
        "[toh,ing]",
        "TNK"
    ],
    "toenails": [
        "[toh,neyl,s]",
        "TNLS"
    ],
    "toes": [
        "['toh', 's']",
        "TS"
    ],
    "together": [
        "['tuh', 'geth', 'er']",
        "TK0R"
    ],
    "toilet": [
        "['toi', 'lit']",
        "TLT"
    ],
    "toke": [
        "[tohk]",
        "TK"
    ],
    "token": [
        "['toh', 'kuhn']",
        "TKN"
    ],
    "tokyo": [
        "['toh', 'kee', 'oh']",
        "TK"
    ],
    "told": [
        "['tohld']",
        "TLT"
    ],
    "tolerance": [
        "[tol,er,uhns]",
        "TLRNS"
    ],
    "toll": [
        "['tohl']",
        "TL"
    ],
    "tolls": [
        "[tohl,s]",
        "TLS"
    ],
    "tom": [
        "['tom']",
        "TM"
    ],
    "tomahawk": [
        "[tom,uh,hawk]",
        "TMHK"
    ],
    "tomato": [
        "[tuh,mey,toh]",
        "TMT"
    ],
    "tomatoes": [
        "[tuh,mey,toh,es]",
        "TMTS"
    ],
    "tomb": [
        "['toom']",
        "TMP"
    ],
    "tombs": [
        "[toom,s]",
        "TMPS"
    ],
    "tombstone": [
        "[toom,stohn]",
        "TMPSTN"
    ],
    "tommy": [
        "['tom', 'ee']",
        "TM"
    ],
    "tomorrow": [
        "['tuh', 'mawr', 'oh']",
        "TMR"
    ],
    "tomorrow's": [
        "['tuh', 'mawr', 'oh', \"'s\"]",
        "TMRS"
    ],
    "ton": [
        "['tuhn']",
        "TN"
    ],
    "tone": [
        "['tohn']",
        "TN"
    ],
    "tones": [
        "[tohn,s]",
        "TNS"
    ],
    "tongue": [
        "['tuhng']",
        "TNK"
    ],
    "tongues": [
        "[tuhng,s]",
        "TNKS"
    ],
    "toni": [
        "['toh', 'nee']",
        "TN"
    ],
    "tonic": [
        "[ton,ik]",
        "TNK"
    ],
    "tonight": [
        "['tuh', 'nahyt']",
        "TNT"
    ],
    "tonight's": [
        "['tuh', 'nahyt', \"'s\"]",
        "TNTTS"
    ],
    "tons": [
        "['tuhn', 's']",
        "TNS"
    ],
    "tony": [
        "['toh', 'nee']",
        "TN"
    ],
    "too": [
        "['too']",
        "T"
    ],
    "took": [
        "['took']",
        "TK"
    ],
    "tool": [
        "['tool']",
        "TL"
    ],
    "tools": [
        "['tool', 's']",
        "TLS"
    ],
    "toon": [
        "[toon]",
        "TN"
    ],
    "toot": [
        "[toot]",
        "TT"
    ],
    "tooth": [
        "['tooth']",
        "T0"
    ],
    "toothpick": [
        "[tooth,pik]",
        "T0PK"
    ],
    "tootsie": [
        "['toot', 'see']",
        "TTS"
    ],
    "top": [
        "['top']",
        "TP"
    ],
    "topic": [
        "['top', 'ik']",
        "TPK"
    ],
    "topless": [
        "['top', 'lis']",
        "TPLS"
    ],
    "topped": [
        "['top', 'ped']",
        "TPT"
    ],
    "topping": [
        "['top', 'ing']",
        "TPNK"
    ],
    "tops": [
        "['tops']",
        "TPS"
    ],
    "torch": [
        "['tawrch']",
        "TRX"
    ],
    "torching": [
        "['tawrch', 'ing']",
        "TRXNK"
    ],
    "tore": [
        "['tawr']",
        "TR"
    ],
    "torn": [
        "['tawrn']",
        "TRN"
    ],
    "tornado": [
        "['tawr', 'ney', 'doh']",
        "TRNT"
    ],
    "toronto": [
        "['tuh', 'ron', 'toh']",
        "TRNT"
    ],
    "torpedo": [
        "[tawr,pee,doh]",
        "TRPT"
    ],
    "torso": [
        "[tawr,soh]",
        "TRS"
    ],
    "tortoise": [
        "['tawr', 'tuhs']",
        "TRTS"
    ],
    "torture": [
        "[tawr,cher]",
        "TRTR"
    ],
    "tortured": [
        "[tawr,cher,d]",
        "TRTRT"
    ],
    "toss": [
        "['taws']",
        "TS"
    ],
    "tossed": [
        "['taws', 'ed']",
        "TST"
    ],
    "tossing": [
        "[taws,ing]",
        "TSNK"
    ],
    "total": [
        "['toht', 'l']",
        "TTL"
    ],
    "totally": [
        "['toht', 'l', 'ee']",
        "TTL"
    ],
    "tote": [
        "['toht']",
        "TT"
    ],
    "totem": [
        "['toh', 'tuhm']",
        "TTM"
    ],
    "toting": [
        "['toh', 'ting']",
        "TTNK"
    ],
    "toucan": [
        "['too', 'kan']",
        "TKN"
    ],
    "touch": [
        "['tuhch']",
        "TX"
    ],
    "touchdown": [
        "['tuhch', 'doun']",
        "TXTN"
    ],
    "touched": [
        "['tuhcht']",
        "TXT"
    ],
    "touches": [
        "[tuhch,es]",
        "TXS"
    ],
    "touching": [
        "['tuhch', 'ing']",
        "TXNK"
    ],
    "tough": [
        "['tuhf']",
        "TF"
    ],
    "tougher": [
        "['tuhf', 'er']",
        "TFR"
    ],
    "toupee": [
        "['too', 'pey']",
        "TP"
    ],
    "tour": [
        "['toor']",
        "TR"
    ],
    "touring": [
        "['toor', 'ing']",
        "TRNK"
    ],
    "tourist": [
        "['toor', 'ist']",
        "TRST"
    ],
    "tourists": [
        "[toor,ist,s]",
        "TRSTS"
    ],
    "tours": [
        "['toor']",
        "TRS"
    ],
    "tow": [
        "['toh']",
        "T"
    ],
    "towed": [
        "['toh', 'ed']",
        "TT"
    ],
    "towel": [
        "['tou', 'uhl']",
        "TL"
    ],
    "towels": [
        "['tou', 'uhl', 's']",
        "TLS"
    ],
    "tower": [
        "['tou', 'er']",
        "TR"
    ],
    "towers": [
        "[tou,er,s]",
        "TRS"
    ],
    "town": [
        "['toun']",
        "TN"
    ],
    "towns": [
        "[toun,s]",
        "TNS"
    ],
    "toxic": [
        "['tok', 'sik']",
        "TKSK"
    ],
    "toy": [
        "['toi']",
        "T"
    ],
    "toying": [
        "['toi', 'ing']",
        "TNK"
    ],
    "toys": [
        "['toi', 's']",
        "TS"
    ],
    "trace": [
        "['treys']",
        "TRS"
    ],
    "track": [
        "['trak']",
        "TRK"
    ],
    "tracking": [
        "[trak,ing]",
        "TRKNK"
    ],
    "tracks": [
        "['trak', 's']",
        "TRKS"
    ],
    "traction": [
        "['trak', 'shuhn']",
        "TRKXN"
    ],
    "tracy": [
        "['trey', 'see']",
        "TRS"
    ],
    "trade": [
        "['treyd']",
        "TRT"
    ],
    "traded": [
        "['treyd', 'd']",
        "TRTT"
    ],
    "tradition": [
        "[truh,dish,uhn]",
        "TRTXN"
    ],
    "traffic": [
        "['traf', 'ik']",
        "TRFK"
    ],
    "trafficking": [
        "['traf', 'ik', 'king']",
        "TRFKNK"
    ],
    "tragedy": [
        "['traj', 'i', 'dee']",
        "TRJT"
    ],
    "tragic": [
        "['traj', 'ik']",
        "TRJK"
    ],
    "trail": [
        "['treyl']",
        "TRL"
    ],
    "trailer": [
        "['trey', 'ler']",
        "TRLR"
    ],
    "train": [
        "['treyn']",
        "TRN"
    ],
    "trained": [
        "['treyn', 'ed']",
        "TRNT"
    ],
    "trainer": [
        "[trey,ner]",
        "TRNR"
    ],
    "training": [
        "['trey', 'ning']",
        "TRNNK"
    ],
    "trains": [
        "[treyn,s]",
        "TRNS"
    ],
    "trait": [
        "[treyt]",
        "TRT"
    ],
    "traitors": [
        "[trey,ter,s]",
        "TRTRS"
    ],
    "traits": [
        "['treyt', 's']",
        "TRTS"
    ],
    "tramp": [
        "['tramp']",
        "TRMP"
    ],
    "trampoline": [
        "['tram', 'puh', 'leen']",
        "TRMPLN"
    ],
    "trance": [
        "['trans']",
        "TRNS"
    ],
    "trans": [
        "['(trns']",
        "TRNS"
    ],
    "transactions": [
        "[tran,sak,shuhn,s]",
        "TRNSKXNS"
    ],
    "transfer": [
        "['verbtrans', 'fur']",
        "TRNSFR"
    ],
    "transform": [
        "['verbtrans', 'fawrm']",
        "TRNSFRM"
    ],
    "transformer": [
        "[trans,fawr,mer]",
        "TRNSFRMR"
    ],
    "transition": [
        "[tran,zish,uhn]",
        "TRNSXN"
    ],
    "translate": [
        "['trans', 'leyt']",
        "TRNSLT"
    ],
    "translation": [
        "['trans', 'ley', 'shuhn']",
        "TRNSLXN"
    ],
    "translations": [
        "['trans', 'ley', 'shuhn', 's']",
        "TRNSLXNS"
    ],
    "translator": [
        "[trans,ley,ter]",
        "TRNSLTR"
    ],
    "translucent": [
        "[trans,loo,suhnt]",
        "TRNSLSNT"
    ],
    "transmission": [
        "['trans', 'mish', 'uhn']",
        "TRNSMSN"
    ],
    "transport": [
        "['verbtrans', 'pawrt']",
        "TRNSPRT"
    ],
    "transportation": [
        "['trans', 'per', 'tey', 'shuhn']",
        "TRNSPRTXN"
    ],
    "transporter": [
        "[trans,pawr,ter]",
        "TRNSPRTR"
    ],
    "trap": [
        "['trap']",
        "TRP"
    ],
    "traphouse": [
        [
            "trap",
            "hous"
        ],
        "TRFS"
    ],
    "trapped": [
        "['trap', 'ped']",
        "TRPT"
    ],
    "trapper": [
        "['trap', 'er']",
        "TRPR"
    ],
    "trappers": [
        "[trap,er,s]",
        "TRPRS"
    ],
    "trapping": [
        "['trap', 'ping']",
        "TRPNK"
    ],
    "traps": [
        "['trap', 's']",
        "TRPS"
    ],
    "trash": [
        "['trash']",
        "TRX"
    ],
    "trauma": [
        "[trou,muh]",
        "TRM"
    ],
    "traumatic": [
        "[truh,mat,ik]",
        "TRMTK"
    ],
    "traumatized": [
        "['trou', 'muh', 'tahyz', 'd']",
        "TRMTST"
    ],
    "travel": [
        "['trav', 'uhl']",
        "TRFL"
    ],
    "traveled": [
        "['trav', 'uhld']",
        "TRFLT"
    ],
    "traveling": [
        "[trav,uhl,ing]",
        "TRFLNK"
    ],
    "travelled": [
        "[trav,uhld]",
        "TRFLT"
    ],
    "travelling": [
        "['trav', 'uhl', 'ling']",
        "TRFLNK"
    ],
    "travels": [
        "[trav,uhl,s]",
        "TRFLS"
    ],
    "tray": [
        "[trey]",
        "TR"
    ],
    "trays": [
        "[trey,s]",
        "TRS"
    ],
    "treacherous": [
        "[trech,er,uhs]",
        "TRXRS"
    ],
    "treadmill": [
        "['tred', 'mil']",
        "TRTML"
    ],
    "treason": [
        "['tree', 'zuhn']",
        "TRSN"
    ],
    "treasure": [
        "['trezh', 'er']",
        "TRSR"
    ],
    "treasures": [
        "['trezh', 'er', 's']",
        "TRSRS"
    ],
    "treat": [
        "['treet']",
        "TRT"
    ],
    "treated": [
        "['treet', 'ed']",
        "TRTT"
    ],
    "treating": [
        "['treet', 'ing']",
        "TRTNK"
    ],
    "treatment": [
        "[treet,muhnt]",
        "TRTMNT"
    ],
    "treats": [
        "['treet', 's']",
        "TRTS"
    ],
    "treble": [
        "[treb,uhl]",
        "TRPL"
    ],
    "tree": [
        "['tree']",
        "TR"
    ],
    "trees": [
        "['tree', 's']",
        "TRS"
    ],
    "trek": [
        "[trek]",
        "TRK"
    ],
    "trench": [
        "['trench']",
        "TRNX"
    ],
    "trenches": [
        "['trench', 'es']",
        "TRNXS"
    ],
    "trend": [
        "['trend']",
        "TRNT"
    ],
    "trending": [
        "['tren', 'ding']",
        "TRNTNK"
    ],
    "trends": [
        "['trend', 's']",
        "TRNTS"
    ],
    "trendsetter": [
        "['trend', 'set', 'er']",
        "TRNTSTR"
    ],
    "trendsetters": [
        "['trend', 'set', 'er', 's']",
        "TRNTSTRS"
    ],
    "trey": [
        "['trey']",
        "TR"
    ],
    "treys": [
        "[trey,s]",
        "TRS"
    ],
    "trial": [
        "['trahy', 'uhl']",
        "TRL"
    ],
    "trials": [
        "[trahy,uhl,s]",
        "TRLS"
    ],
    "tribe": [
        "['trahyb']",
        "TRP"
    ],
    "tribes": [
        "[trahyb,s]",
        "TRPS"
    ],
    "tribulations": [
        "[trib,yuh,ley,shuhn,s]",
        "TRPLXNS"
    ],
    "triceps": [
        "[trahy,seps]",
        "TRSPS"
    ],
    "triceratops": [
        "[trahy,ser,uh,tops]",
        "TRSRTPS"
    ],
    "trick": [
        "['trik']",
        "TRK"
    ],
    "tricked": [
        "['trik', 'ed']",
        "TRKT"
    ],
    "trickery": [
        "['trik', 'uh', 'ree']",
        "TRKR"
    ],
    "tricking": [
        "['trik', 'ing']",
        "TRKNK"
    ],
    "trickle": [
        "[trik,uhl]",
        "TRKL"
    ],
    "tricks": [
        "['trik', 's']",
        "TRKS"
    ],
    "tricky": [
        "[trik,ee]",
        "TRK"
    ],
    "tried": [
        "['trahyd']",
        "TRT"
    ],
    "tries": [
        "['trahyz']",
        "TRS"
    ],
    "trifling": [
        "[trahy,fling]",
        "TRFLNK"
    ],
    "trigger": [
        "['trig', 'er']",
        "TRKR"
    ],
    "triggers": [
        "['trig', 'er', 's']",
        "TRKRS"
    ],
    "trill": [
        "['tril']",
        "TRL"
    ],
    "trillion": [
        "['tril', 'yuhn']",
        "TRLN"
    ],
    "trim": [
        "[trim]",
        "TRM"
    ],
    "trimmed": [
        "['trim', 'med']",
        "TRMT"
    ],
    "trinidad": [
        "[trin,i,dad]",
        "TRNTT"
    ],
    "trinity": [
        "['trin', 'i', 'tee']",
        "TRNT"
    ],
    "trio": [
        "[tree,oh]",
        "TR"
    ],
    "trip": [
        "['trip']",
        "TRP"
    ],
    "triple": [
        "['trip', 'uhl']",
        "TRPL"
    ],
    "tripled": [
        "[trip,uhl,d]",
        "TRPLT"
    ],
    "tripped": [
        "[trip,ped]",
        "TRPT"
    ],
    "tripping": [
        "['trip', 'ing']",
        "TRPNK"
    ],
    "trips": [
        "['trip', 's']",
        "TRPS"
    ],
    "triumph": [
        "[trahy,uhmf]",
        "TRMF"
    ],
    "trois": [
        "['trwah']",
        "TR"
    ],
    "trojan": [
        "['troh', 'juhn']",
        "TRJN"
    ],
    "trojans": [
        "['troh', 'juhn', 's']",
        "TRJNS"
    ],
    "trolling": [
        "['trohl', 'ing']",
        "TRLNK"
    ],
    "troop": [
        "['troop']",
        "TRP"
    ],
    "trooper": [
        "['troo', 'per']",
        "TRPR"
    ],
    "troopers": [
        "['troo', 'per', 's']",
        "TRPRS"
    ],
    "troops": [
        "['troop', 's']",
        "TRPS"
    ],
    "tropes": [
        "[trohp,s]",
        "TRPS"
    ],
    "trophy": [
        "['troh', 'fee']",
        "TRF"
    ],
    "tropic": [
        "[trop,ik]",
        "TRPK"
    ],
    "tropical": [
        "['trop', 'i', 'kuhlfor14']",
        "TRPKL"
    ],
    "tropicana": [
        [
            "trop",
            "ik",
            "an",
            "uh"
        ],
        "TRPKN"
    ],
    "tropics": [
        "['trop', 'ik', 's']",
        "TRPKS"
    ],
    "trot": [
        "[trot]",
        "TRT"
    ],
    "trotter": [
        "[trot,er]",
        "TRTR"
    ],
    "trouble": [
        "['truhb', 'uhl']",
        "TRPL"
    ],
    "troubled": [
        "[truhb,uhl,d]",
        "TRPLT"
    ],
    "troublemaker": [
        "[truhb,uhl,mey,ker]",
        "TRPLMKR"
    ],
    "troubles": [
        "[truhb,uhl,s]",
        "TRPLS"
    ],
    "trough": [
        "[trawf]",
        "TRF"
    ],
    "trousers": [
        "['trou', 'zerz']",
        "TRSRS"
    ],
    "trout": [
        "['trout']",
        "TRT"
    ],
    "troy": [
        "[troi]",
        "TR"
    ],
    "truancy": [
        "['troo', 'uhn', 'see']",
        "TRNS"
    ],
    "truce": [
        "[troos]",
        "TRS"
    ],
    "truck": [
        "['truhk']",
        "TRK"
    ],
    "trucker": [
        "['truhk', 'er']",
        "TRKR"
    ],
    "trucking": [
        "[truhk,ing]",
        "TRKNK"
    ],
    "truckload": [
        "['truhk', 'lohd']",
        "TRKLT"
    ],
    "trucks": [
        "['truhk', 's']",
        "TRKS"
    ],
    "true": [
        "['troo']",
        "TR"
    ],
    "trues": [
        "[troo,s]",
        "TRS"
    ],
    "truest": [
        "[troo,st]",
        "TRST"
    ],
    "truly": [
        "['troo', 'lee']",
        "TRL"
    ],
    "trump": [
        "['truhmp']",
        "TRMP"
    ],
    "trumpet": [
        "[truhm,pit]",
        "TRMPT"
    ],
    "trumpets": [
        "[truhm,pits]",
        "TRMPTS"
    ],
    "trunk": [
        "['truhngk']",
        "TRNK"
    ],
    "trunks": [
        "[truhngk,s]",
        "TRNKS"
    ],
    "trust": [
        "['truhst']",
        "TRST"
    ],
    "trusting": [
        "['truhs', 'ting']",
        "TRSTNK"
    ],
    "truth": [
        "['trooth']",
        "TR0"
    ],
    "truthful": [
        "[trooth,fuhl]",
        "TR0FL"
    ],
    "truthfully": [
        "['trooth', 'fuhl', 'ly']",
        "TR0FL"
    ],
    "truths": [
        "[trooth,s]",
        "TR0S"
    ],
    "try": [
        "['trahy']",
        "TR"
    ],
    "trying": [
        "['trahy', 'ing']",
        "TRNK"
    ],
    "tsunami": [
        "[tsoo,nah,mee]",
        "TSNM"
    ],
    "tub": [
        "['tuhb']",
        "TP"
    ],
    "tube": [
        "[toob]",
        "TP"
    ],
    "tubes": [
        "[toob,s]",
        "TPS"
    ],
    "tubs": [
        "[tuhb,s]",
        "TPS"
    ],
    "tuck": [
        "['tuhk']",
        "TK"
    ],
    "tucked": [
        "['tuhk', 'ed']",
        "TKT"
    ],
    "tucker": [
        "['tuhk', 'er']",
        "TKR"
    ],
    "tucking": [
        "['tuhk', 'ing']",
        "TKNK"
    ],
    "tuesday": [
        "['tooz', 'dey']",
        "TST"
    ],
    "tuesdays": [
        "[tooz,deyz]",
        "TSTS"
    ],
    "tug": [
        "[tuhg]",
        "TK"
    ],
    "tugging": [
        "[tuhg,ging]",
        "TKNK"
    ],
    "tuition": [
        "['too', 'ish', 'uhn']",
        "TXN"
    ],
    "tumbling": [
        "[tuhm,bling]",
        "TMPLNK"
    ],
    "tummy": [
        "['tuhm', 'ee']",
        "TM"
    ],
    "tumor": [
        "['too', 'mer']",
        "TMR"
    ],
    "tune": [
        "['toon']",
        "TN"
    ],
    "tunechi": [
        [
            "toon",
            "ne",
            "chee"
        ],
        "TNX"
    ],
    "tuned": [
        "[toon,d]",
        "TNT"
    ],
    "tuner": [
        "['too', 'ner']",
        "TNR"
    ],
    "tunes": [
        "[toon,s]",
        "TNS"
    ],
    "tunnel": [
        "['tuhn', 'l']",
        "TNL"
    ],
    "tunnels": [
        "[tuhn,l,s]",
        "TNLS"
    ],
    "turban": [
        "['tur', 'buhn']",
        "TRPN"
    ],
    "turbo": [
        "['tur', 'boh']",
        "TRP"
    ],
    "turbos": [
        "['tur', 'boh', 's']",
        "TRPS"
    ],
    "turbulence": [
        "['tur', 'byuh', 'luhns']",
        "TRPLNS"
    ],
    "turd": [
        "['turd']",
        "TRT"
    ],
    "turds": [
        "[turd,s]",
        "TRTS"
    ],
    "turf": [
        "['turf']",
        "TRF"
    ],
    "turk": [
        "[turk]",
        "TRK"
    ],
    "turkey": [
        "['tur', 'kee']",
        "TRK"
    ],
    "turkeys": [
        "[tur,kee,s]",
        "TRKS"
    ],
    "turks": [
        "[turk,s]",
        "TRKS"
    ],
    "turmoil": [
        "['tur', 'moil']",
        "TRML"
    ],
    "turn": [
        "['turn']",
        "TRN"
    ],
    "turned": [
        "['turn', 'ed']",
        "TRNT"
    ],
    "turner": [
        "['tur', 'ner']",
        "TRNR"
    ],
    "turning": [
        "['tur', 'ning']",
        "TRNNK"
    ],
    "turnpike": [
        "[turn,pahyk]",
        "TRNPK"
    ],
    "turns": [
        "['turn', 's']",
        "TRNS"
    ],
    "turnt": [
        [
            "turnt"
        ],
        "TRNT"
    ],
    "turpentine": [
        "[tur,puhn,tahyn]",
        "TRPNTN"
    ],
    "turtle": [
        "['tur', 'tl']",
        "TRTL"
    ],
    "turtles": [
        "[tur,tl,s]",
        "TRTLS"
    ],
    "tush": [
        "[tuhsh]",
        "TX"
    ],
    "tusk": [
        "['tuhsk']",
        "TSK"
    ],
    "tussle": [
        "[tuhs,uhl]",
        "TSL"
    ],
    "tut": [
        "['pronouncedasanalveolarclick']",
        "TT"
    ],
    "tutor": [
        "['too', 'ter']",
        "TTR"
    ],
    "tutu": [
        "[too,too]",
        "TT"
    ],
    "tux": [
        "['tuhks']",
        "TKS"
    ],
    "tuxedo": [
        "[tuhk,see,doh]",
        "TKST"
    ],
    "tuxedos": [
        "[tuhk,see,doh,s]",
        "TKSTS"
    ],
    "tuxes": [
        "[tuhks,es]",
        "TKSS"
    ],
    "tv": [
        "['tee', 'vee']",
        "TF"
    ],
    "tv's": [
        "['tee', 'vee', \"'s\"]",
        "TFFS"
    ],
    "twain": [
        "[tweyn]",
        "TN"
    ],
    "twat": [
        "[twaht]",
        "TT"
    ],
    "tweak": [
        "['tweek']",
        "TK"
    ],
    "tweaked": [
        "[tweek,ed]",
        "TKT"
    ],
    "tweaking": [
        "['tweek', 'ing']",
        "TKNK"
    ],
    "tweet": [
        "[tweet]",
        "TT"
    ],
    "tweeters": [
        "[twee,ter,s]",
        "TTRS"
    ],
    "tweeting": [
        "[tweet,ing]",
        "TTNK"
    ],
    "tweets": [
        "[tweet,s]",
        "TTS"
    ],
    "twelve": [
        "['twelv']",
        "TLF"
    ],
    "twenties": [
        [
            "twen",
            "tees"
        ],
        "TNTS"
    ],
    "twenty": [
        "['twen', 'tee']",
        "TNT"
    ],
    "twerking": [
        "['twurk', 'ing']",
        "TRKNK"
    ],
    "twice": [
        "['twahys']",
        "TS"
    ],
    "twilight": [
        "[twahy,lahyt]",
        "TLT"
    ],
    "twin": [
        "['twin']",
        "TN"
    ],
    "twinkle": [
        "['twing', 'kuhl']",
        "TNKL"
    ],
    "twins": [
        "['twin', 's']",
        "TNS"
    ],
    "twirl": [
        "[twurl]",
        "TRL"
    ],
    "twist": [
        "['twist']",
        "TST"
    ],
    "twisted": [
        "['twist', 'ed']",
        "TSTT"
    ],
    "twister": [
        "[twis,ter]",
        "TSTR"
    ],
    "twisting": [
        "['twis', 'ting']",
        "TSTNK"
    ],
    "twitch": [
        "['twich']",
        "TX"
    ],
    "twitching": [
        "['twich', 'ing']",
        "TXNK"
    ],
    "twitter": [
        "['twit', 'er']",
        "TTR"
    ],
    "two": [
        "['too']",
        "T"
    ],
    "two's": [
        "[too,'s]",
        "TS"
    ],
    "twos": [
        "['too', 's']",
        "TS"
    ],
    "tycoon": [
        "['tahy', 'koon']",
        "TKN"
    ],
    "tying": [
        "['tahy', 'ing']",
        "TNK"
    ],
    "tylenol": [
        "['tahy', 'luh', 'nawl']",
        "TLNL"
    ],
    "tyler": [
        "['tahy', 'ler']",
        "TLR"
    ],
    "type": [
        "['tahyp']",
        "TP"
    ],
    "types": [
        "['tahyp', 's']",
        "TPS"
    ],
    "typhoon": [
        "['tahy', 'foon']",
        "TFN"
    ],
    "typical": [
        "['tip', 'i', 'kuhl']",
        "TPKL"
    ],
    "typo": [
        "[tahy,poh]",
        "TP"
    ],
    "tyson": [
        "['tahy', 'suhn']",
        "TSN"
    ],
    "ufo": [
        "['yoo', 'ef', 'ohor']",
        "AF"
    ],
    "uganda": [
        "[yoo,gan,duh]",
        "AKNT"
    ],
    "ugly": [
        "['uhg', 'lee']",
        "AKL"
    ],
    "uh": [
        "['uh']",
        "A"
    ],
    "um": [
        "['uhm']",
        "AM"
    ],
    "umbilical": [
        "[uhm,bil,i,kuhl]",
        "AMPLKL"
    ],
    "umbrella": [
        "['uhm', 'brel', 'uh']",
        "AMPRL"
    ],
    "umbrellas": [
        "[uhm,brel,uh,s]",
        "AMPRLS"
    ],
    "umma": [
        "[uhm,uh,]",
        "AM"
    ],
    "umpire": [
        "['uhm', 'pahyuhr']",
        "AMPR"
    ],
    "un": [
        "['uhn']",
        "AN"
    ],
    "unattractive": [
        "[un-,uh,trak,tiv]",
        "ANTRKTF"
    ],
    "unbelievable": [
        "[uhn,bi,lee,vuh,buhl]",
        "ANPLFPL"
    ],
    "unbreakable": [
        "[un-able,breyk]",
        "ANPRKPL"
    ],
    "unbutton": [
        "[uhn,buht,n]",
        "ANPTN"
    ],
    "uncle": [
        "['uhng', 'kuhl']",
        "ANKL"
    ],
    "uncle's": [
        "[uhng,kuhl,'s]",
        "ANKLS"
    ],
    "uncles": [
        "['uhng', 'kuhl', 's']",
        "ANKLS"
    ],
    "uncomfortable": [
        "['uhn', 'kuhmf', 'tuh', 'buhl']",
        "ANKMFRTPL"
    ],
    "unconditional": [
        "[uhn,kuhn,dish,uh,nl]",
        "ANKNTXNL"
    ],
    "uncouth": [
        "[uhn,kooth]",
        "ANK0"
    ],
    "uncut": [
        "['uhn', 'kuht']",
        "ANKT"
    ],
    "undefeated": [
        "[un-ed,dih,feet]",
        "ANTFTT"
    ],
    "under": [
        "['uhn', 'der']",
        "ANTR"
    ],
    "underage": [
        "[uhn,der,eyj]",
        "ANTRJ"
    ],
    "underarm": [
        "[uhn,der,ahrm]",
        "ANTRRM"
    ],
    "underarms": [
        "['uhn', 'der', 'ahrm', 's']",
        "ANTRRMS"
    ],
    "undercover": [
        "['uhn', 'der', 'kuhv', 'er']",
        "ANTRKFR"
    ],
    "underdog": [
        "[uhn,der,dawg]",
        "ANTRTK"
    ],
    "underestimate": [
        "[verbuhn,der,es,tuh,meyt]",
        "ANTRSTMT"
    ],
    "underestimated": [
        "[verbuhn,der,es,tuh,meyt,d]",
        "ANTRSTMTT"
    ],
    "underground": [
        "['adverb']",
        "ANTRKRNT"
    ],
    "underneath": [
        "[uhn,der,neeth]",
        "ANTRN0"
    ],
    "underrated": [
        "['uhn', 'der', 'reyt', 'd']",
        "ANTRTT"
    ],
    "understand": [
        "['uhn', 'der', 'stand']",
        "ANTRSTNT"
    ],
    "understanding": [
        "[uhn,der,stan,ding]",
        "ANTRSTNTNK"
    ],
    "understands": [
        "[uhn,der,stand,s]",
        "ANTRSTNTS"
    ],
    "understood": [
        "['uhn', 'der', 'stood']",
        "ANTRSTT"
    ],
    "undertaker": [
        "['uhn', 'der', 'tey', 'kerfor1uhn']",
        "ANTRTKR"
    ],
    "underwater": [
        "['uhn', 'der', 'waw', 'ter']",
        "ANTRTR"
    ],
    "underwear": [
        "['uhn', 'der', 'wair']",
        "ANTRR"
    ],
    "underworld": [
        "['uhn', 'der', 'wurld']",
        "ANTRRLT"
    ],
    "undeveloped": [
        "[uhn,di,vel,uhpt]",
        "ANTFLPT"
    ],
    "undisputed": [
        "[un-d,dih,spyoot]",
        "ANTSPTT"
    ],
    "undivided": [
        "[un-,dih,vahy,did]",
        "ANTFTT"
    ],
    "undone": [
        "[uhn,duhn]",
        "ANTN"
    ],
    "undress": [
        "[uhn,dres]",
        "ANTRS"
    ],
    "undressed": [
        "[uhn,drest]",
        "ANTRST"
    ],
    "undressing": [
        "['uhn', 'dres', 'ing']",
        "ANTRSNK"
    ],
    "unearthly": [
        "[uhn,urth,lee]",
        "ANR0L"
    ],
    "unemployed": [
        "['uhn', 'em', 'ploid']",
        "ANMPLT"
    ],
    "unexpected": [
        "[uhn,ik,spek,tid]",
        "ANKSPKTT"
    ],
    "unfair": [
        "[uhn,fair]",
        "ANFR"
    ],
    "unfaithful": [
        "[uhn,feyth,fuhl]",
        "ANF0FL"
    ],
    "unfold": [
        "['uhn', 'fohld']",
        "ANFLT"
    ],
    "unforgettable": [
        "[uhn,fer,get,uh,buhl]",
        "ANFRKTPL"
    ],
    "unforgiving": [
        "[uhn,fer,giv,ing]",
        "ANFRJFNK"
    ],
    "unfortunate": [
        "['uhn', 'fawr', 'chuh', 'nit']",
        "ANFRTNT"
    ],
    "unfortunately": [
        "[uhn,fawr,chuh,nit,ly]",
        "ANFRTNTL"
    ],
    "unhealthy": [
        "[uhn,hel,thee]",
        "ANL0"
    ],
    "unheard": [
        "[uhn,hurd]",
        "ANRT"
    ],
    "unicorn": [
        "[yoo,ni,kawrn]",
        "ANKRN"
    ],
    "uniform": [
        "['yoo', 'nuh', 'fawrm']",
        "ANFRM"
    ],
    "uninvited": [
        "[un-d,verbin,vahyt]",
        "ANNFTT"
    ],
    "union": [
        "[yoon,yuhn]",
        "ANN"
    ],
    "unique": [
        "['yoo', 'neek']",
        "ANK"
    ],
    "unit": [
        "['yoo', 'nit']",
        "ANT"
    ],
    "united": [
        "[yoo,nahy,tid]",
        "ANTT"
    ],
    "units": [
        "[yoo,nit,s]",
        "ANTS"
    ],
    "unity": [
        "['yoo', 'ni', 'tee']",
        "ANT"
    ],
    "universal": [
        "['yoo', 'nuh', 'vur', 'suhl']",
        "ANFRSL"
    ],
    "universe": [
        "['yoo', 'nuh', 'vurs']",
        "ANFRS"
    ],
    "university": [
        "[yoo,nuh,vur,si,tee]",
        "ANFRST"
    ],
    "unkind": [
        "[uhn,kahynd]",
        "ANKNT"
    ],
    "unknown": [
        "[uhn,nohn]",
        "ANKNN"
    ],
    "unleaded": [
        "['uhn', 'led', 'id']",
        "ANLTT"
    ],
    "unleash": [
        "[uhn,leesh]",
        "ANLX"
    ],
    "unless": [
        "['uhn', 'les']",
        "ANLS"
    ],
    "unlike": [
        "['uhn', 'lahyk']",
        "ANLK"
    ],
    "unlikely": [
        "[uhn,lahyk,lee]",
        "ANLKL"
    ],
    "unlimited": [
        "[uhn,lim,i,tid]",
        "ANLMTT"
    ],
    "unload": [
        "['uhn', 'lohd']",
        "ANLT"
    ],
    "unlock": [
        "['uhn', 'lok']",
        "ANLK"
    ],
    "unlocked": [
        "['uhn', 'lok', 'ed']",
        "ANLKT"
    ],
    "unlucky": [
        "[uhn,luhk,ee]",
        "ANLK"
    ],
    "unplug": [
        "[uhn,pluhg]",
        "ANPLK"
    ],
    "unplugged": [
        "[uhn,pluhg,ged]",
        "ANPLKT"
    ],
    "unpredictable": [
        "[uhn,pri,dik,tuh,buhl]",
        "ANPRTKTPL"
    ],
    "unraveling": [
        "[uhn,rav,uhl,ing]",
        "ANRFLNK"
    ],
    "unreal": [
        "[uhn,ree,uhl]",
        "ANRL"
    ],
    "unruly": [
        "['uhn', 'roo', 'lee']",
        "ANRL"
    ],
    "unspoken": [
        "[uhn,spoh,kuhn]",
        "ANSPKN"
    ],
    "unstable": [
        "[uhn,stey,buhl]",
        "ANSTPL"
    ],
    "unstoppable": [
        "['uhn', 'stop', 'uh', 'buhl']",
        "ANSTPPL"
    ],
    "unsure": [
        "[uhn,shoor]",
        "ANSR"
    ],
    "untamed": [
        "['un-d', 'teym']",
        "ANTMT"
    ],
    "unthinkable": [
        "[uhn,thing,kuh,buhl]",
        "AN0NKPL"
    ],
    "until": [
        "['uhn', 'til']",
        "ANTL"
    ],
    "unto": [
        "['uhn', 'too']",
        "ANT"
    ],
    "untouchable": [
        "[uhn,tuhch,uh,buhl]",
        "ANTXPL"
    ],
    "untucked": [
        "['uhn', 'tuhk', 'ed']",
        "ANTKT"
    ],
    "unusual": [
        "[uhn,yoo,zhoo,uhl]",
        "ANSL"
    ],
    "unwind": [
        "['uhn', 'wahynd']",
        "ANNT"
    ],
    "unworthy": [
        "['uhn', 'wur', 'thee']",
        "ANR0"
    ],
    "unwrap": [
        "[uhn,rap]",
        "ANRP"
    ],
    "up": [
        "['uhp']",
        "AP"
    ],
    "up's": [
        "['uhp', \"'s\"]",
        "APPS"
    ],
    "upgrade": [
        "['nounuhp', 'greyd']",
        "APKRT"
    ],
    "upgraded": [
        "['nounuhp', 'greyd', 'd']",
        "APKRTT"
    ],
    "upholstered": [
        "[uhp,hohl,ster,ed]",
        "AFLSTRT"
    ],
    "upon": [
        "['uh', 'pon']",
        "APN"
    ],
    "upper": [
        "['uhp', 'er']",
        "APR"
    ],
    "uppercut": [
        "[uhp,er,kuht]",
        "APRKT"
    ],
    "ups": [
        "['uhp']",
        "APS"
    ],
    "upset": [
        "['verb']",
        "APST"
    ],
    "upside": [
        "['uhp', 'sahyd']",
        "APST"
    ],
    "upstairs": [
        "['uhp', 'stairz']",
        "APSTRS"
    ],
    "uptight": [
        "[uhp,tahyt]",
        "APTT"
    ],
    "uptown": [
        "['adverb']",
        "APTN"
    ],
    "ur": [
        "['ur']",
        "AR"
    ],
    "urban": [
        "[ur,buhn]",
        "ARPN"
    ],
    "urge": [
        "[urj]",
        "ARJ"
    ],
    "urgent": [
        "['ur', 'juhnt']",
        "ARJNT"
    ],
    "urine": [
        "['yoor', 'in']",
        "ARN"
    ],
    "urn": [
        "[urn]",
        "ARN"
    ],
    "us": [
        "['uhs']",
        "AS"
    ],
    "usa": [
        [
            "yoo",
            "es",
            "ey"
        ],
        "AS"
    ],
    "use": [
        "['verbyoozorforptformof9']",
        "AS"
    ],
    "used": [
        "['yoozdorfor4']",
        "AST"
    ],
    "useless": [
        "[yoos,lis]",
        "ASLS"
    ],
    "user": [
        "[yoo,zer]",
        "ASR"
    ],
    "usher": [
        "['uhsh', 'er']",
        "AXR"
    ],
    "using": [
        [
            "yooz",
            "ing"
        ],
        "ASNK"
    ],
    "usual": [
        "['yoo', 'zhoo', 'uhl']",
        "ASL"
    ],
    "usually": [
        "['yoo', 'zhoo', 'uhl', 'ly']",
        "ASL"
    ],
    "utter": [
        "[uht,er]",
        "ATR"
    ],
    "utterly": [
        "[uht,er,lee]",
        "ATRL"
    ],
    "uzi": [
        "['oo', 'zee']",
        "AS"
    ],
    "uzi's": [
        "[oo,zee,'s]",
        "ASS"
    ],
    "uzis": [
        "['oo', 'zee', 's']",
        "ASS"
    ],
    "v": [
        "['vee', '']",
        "F"
    ],
    "v's": [
        [
            "vee",
            "es"
        ],
        "FFS"
    ],
    "vacancy": [
        "[vey,kuhn,see]",
        "FKNS"
    ],
    "vacant": [
        "['vey', 'kuhnt']",
        "FKNT"
    ],
    "vacate": [
        "[vey,keytor]",
        "FKT"
    ],
    "vacation": [
        "['vey', 'key', 'shuhn']",
        "FKXN"
    ],
    "vacations": [
        "[vey,key,shuhn,s]",
        "FKXNS"
    ],
    "vacay": [
        "['vey', 'key']",
        "FK"
    ],
    "vaccine": [
        "[vak,seenor]",
        "FXN"
    ],
    "vacuum": [
        "['vak', 'yoom']",
        "FKM"
    ],
    "vagina": [
        "[vuh,jahy,nuh]",
        "FJN"
    ],
    "vain": [
        "['veyn']",
        "FN"
    ],
    "valentine": [
        "[val,uhn,tahyn]",
        "FLNTN"
    ],
    "valentine's": [
        "[val,uhn,tahyn,'s]",
        "FLNTNS"
    ],
    "valentines": [
        "[val,uhn,tahyn,s]",
        "FLNTNS"
    ],
    "valet": [
        "['va', 'ley']",
        "FLT"
    ],
    "valid": [
        "[val,id]",
        "FLT"
    ],
    "valley": [
        "['val', 'ee']",
        "FL"
    ],
    "valuable": [
        "[val,yoo,uh,buhl]",
        "FLPL"
    ],
    "value": [
        "['val', 'yoo']",
        "FL"
    ],
    "valued": [
        "[val,yood]",
        "FLT"
    ],
    "values": [
        "[val,yoo,s]",
        "FLS"
    ],
    "valve": [
        "[valv]",
        "FLF"
    ],
    "vamoose": [
        "[va,moos]",
        "FMS"
    ],
    "vamp": [
        "[vamp]",
        "FMP"
    ],
    "vampire": [
        "['vam', 'pahyuhr']",
        "FMPR"
    ],
    "vampires": [
        "['vam', 'pahyuhr', 's']",
        "FMPRS"
    ],
    "vamps": [
        "['vamp', 's']",
        "FMPS"
    ],
    "van": [
        "['van']",
        "FN"
    ],
    "vandal": [
        "[van,dl]",
        "FNTL"
    ],
    "vanessa": [
        "[vuh,nes,uh]",
        "FNS"
    ],
    "vanilla": [
        "['vuh', 'nil', 'uhor']",
        "FNL"
    ],
    "vanish": [
        "['van', 'ish']",
        "FNX"
    ],
    "vanished": [
        "[van,ish,ed]",
        "FNXT"
    ],
    "vanity": [
        "['van', 'i', 'tee']",
        "FNT"
    ],
    "vans": [
        "['van', 's']",
        "FNS"
    ],
    "vapors": [
        "['vey', 'per', 's']",
        "FPRS"
    ],
    "vapours": [
        "[vey,per,s]",
        "FPRS"
    ],
    "varsity": [
        "[vahr,si,tee]",
        "FRST"
    ],
    "vas": [
        "[vas]",
        "FS"
    ],
    "vase": [
        "[veys]",
        "FS"
    ],
    "vaseline": [
        "[vas,uh,leen]",
        "FSLN"
    ],
    "vault": [
        "['vawlt']",
        "FLT"
    ],
    "vegan": [
        "['vee', 'guhn']",
        "FKN"
    ],
    "vegas": [
        "['vee', 'guh', 's']",
        "FKS"
    ],
    "vegetable": [
        "[vej,tuh,buhl]",
        "FKTPL"
    ],
    "vegetables": [
        "['vej', 'tuh', 'buhl', 's']",
        "FKTPLS"
    ],
    "vegetarian": [
        "['vej', 'i', 'tair', 'ee', 'uhn']",
        "FKTRN"
    ],
    "vehicle": [
        "[vee,i,kuhlor]",
        "FHKL"
    ],
    "vehicles": [
        "['vee', 'i', 'kuhlor', 's']",
        "FHKLS"
    ],
    "vehicular": [
        "[vee,hik,yuh,ler]",
        "FHKLR"
    ],
    "vein": [
        "['veyn']",
        "FN"
    ],
    "veins": [
        "['veyn', 's']",
        "FNS"
    ],
    "velcro": [
        "[vel,kroh]",
        "FLKR"
    ],
    "velour": [
        "['vuh', 'loor']",
        "FLR"
    ],
    "velvet": [
        "[vel,vit]",
        "FLFT"
    ],
    "vendetta": [
        "['ven', 'det', 'uh']",
        "FNTT"
    ],
    "vending": [
        "[vend,ing]",
        "FNTNK"
    ],
    "veneers": [
        "[vuh,neer,s]",
        "FNRS"
    ],
    "venereal": [
        "['vuh', 'neer', 'ee', 'uhl']",
        "FNRL"
    ],
    "venezuela": [
        "['ven', 'uh', 'zwey', 'luh']",
        "FNSL"
    ],
    "venice": [
        "[ven,is]",
        "FNS"
    ],
    "venom": [
        "['ven', 'uhm']",
        "FNM"
    ],
    "vent": [
        "['vent']",
        "FNT"
    ],
    "ventilation": [
        "['ven', 'tl', 'ey', 'shuhn']",
        "FNTLXN"
    ],
    "venues": [
        "[ven,yoo,s]",
        "FNS"
    ],
    "venus": [
        "['vee', 'nuhs']",
        "FNS"
    ],
    "vera": [
        "['ver', 'uh']",
        "FR"
    ],
    "verb": [
        "[vurb]",
        "FRP"
    ],
    "verbal": [
        "[vur,buhl]",
        "FRPL"
    ],
    "verbs": [
        "[vurb,s]",
        "FRPS"
    ],
    "verdict": [
        "['vur', 'dikt']",
        "FRTKT"
    ],
    "verge": [
        "['vurj']",
        "FRJ"
    ],
    "veronica": [
        "[vuh,ron,i,kuh]",
        "FRNK"
    ],
    "versatile": [
        "['vur', 'suh', 'tlor']",
        "FRSTL"
    ],
    "verse": [
        "['vurs']",
        "FRS"
    ],
    "verses": [
        "['vurs', 's']",
        "FRSS"
    ],
    "version": [
        "['vur', 'zhuhn']",
        "FRSN"
    ],
    "versus": [
        "['vur', 'suhs']",
        "FRSS"
    ],
    "vert": [
        "['vurt']",
        "FRT"
    ],
    "vertical": [
        "[vur,ti,kuhl]",
        "FRTKL"
    ],
    "very": [
        "['ver', 'ee']",
        "FR"
    ],
    "vessel": [
        "[ves,uhl]",
        "FSL"
    ],
    "vest": [
        "['vest']",
        "FST"
    ],
    "vet": [
        "['vet']",
        "FT"
    ],
    "veteran": [
        "['vet', 'er', 'uhn']",
        "FTRN"
    ],
    "veterans": [
        "[vet,er,uhn,s]",
        "FTRNS"
    ],
    "vets": [
        "[vet,s]",
        "FTS"
    ],
    "via": [
        "['vahy', 'uh']",
        "F"
    ],
    "viagra": [
        "['vahy', 'ag', 'ruh']",
        "FKR"
    ],
    "vibe": [
        "['vahyb']",
        "FP"
    ],
    "vibes": [
        "['vahybz']",
        "FPS"
    ],
    "vibrant": [
        "[vahy,bruhnt]",
        "FPRNT"
    ],
    "vibrate": [
        "['vahy', 'breyt']",
        "FPRT"
    ],
    "vibrations": [
        "[vahy,brey,shuhn,s]",
        "FPRXNS"
    ],
    "vice": [
        "[vahys]",
        "FS"
    ],
    "vices": [
        "['vahys', 's']",
        "FSS"
    ],
    "vicinity": [
        "[vi,sin,i,tee]",
        "FSNT"
    ],
    "vicious": [
        "['vish', 'uhs']",
        "FSS"
    ],
    "vick": [
        "['vik']",
        "FK"
    ],
    "vicodin": [
        "['vahy', 'kuh', 'din']",
        "FKTN"
    ],
    "victim": [
        "['vik', 'tim']",
        "FKTM"
    ],
    "victims": [
        "[vik,tim,s]",
        "FKTMS"
    ],
    "victor": [
        "[vik,ter]",
        "FKTR"
    ],
    "victoria": [
        "['vik', 'tawr', 'ee', 'uh']",
        "FKTR"
    ],
    "victoria's": [
        "[vik,tawr,ee,uh,'s]",
        "FKTRS"
    ],
    "victorious": [
        "['vik', 'tawr', 'ee', 'uhs']",
        "FKTRS"
    ],
    "victory": [
        "['vik', 'tuh', 'ree']",
        "FKTR"
    ],
    "video": [
        "['vid', 'ee', 'oh']",
        "FT"
    ],
    "videos": [
        "['vid', 'ee', 'oh', 's']",
        "FTS"
    ],
    "vie": [
        "[vahy]",
        "F"
    ],
    "vietnam": [
        "['vee', 'et', 'nahm']",
        "FTNM"
    ],
    "view": [
        "['vyoo']",
        "F"
    ],
    "viewed": [
        "[vyoo,ed]",
        "FT"
    ],
    "viewing": [
        "['vyoo', 'ing']",
        "FNK"
    ],
    "views": [
        "['vyoo', 's']",
        "FS"
    ],
    "viking": [
        "['vahy', 'king']",
        "FKNK"
    ],
    "villa": [
        "[vil,uh]",
        "FL"
    ],
    "village": [
        "['vil', 'ij']",
        "FLJ"
    ],
    "villain": [
        "['vil', 'uhn']",
        "FLN"
    ],
    "villains": [
        "['vil', 'uhn', 's']",
        "FLNS"
    ],
    "ville": [
        [
            "vee",
            "leh"
        ],
        "FL"
    ],
    "vine": [
        "[vahyn]",
        "FN"
    ],
    "vino": [
        "[vee,noh]",
        "FN"
    ],
    "vintage": [
        "['vin', 'tij']",
        "FNTJ"
    ],
    "vinyl": [
        "[vahyn,l]",
        "FNL"
    ],
    "violate": [
        "['vahy', 'uh', 'leyt']",
        "FLT"
    ],
    "violated": [
        "[vahy,uh,leyt,d]",
        "FLTT"
    ],
    "violation": [
        "['vahy', 'uh', 'ley', 'shuhn']",
        "FLXN"
    ],
    "violations": [
        "[vahy,uh,ley,shuhn,s]",
        "FLXNS"
    ],
    "violence": [
        "['vahy', 'uh', 'luhns']",
        "FLNS"
    ],
    "violent": [
        "['vahy', 'uh', 'luhnt']",
        "FLNT"
    ],
    "violets": [
        "['vahy', 'uh', 'lit', 's']",
        "FLTS"
    ],
    "violin": [
        "['vahy', 'uh', 'lin']",
        "FLN"
    ],
    "violins": [
        "['vahy', 'uh', 'lin', 's']",
        "FLNS"
    ],
    "vip": [
        "['vee', 'ahy', 'pee']",
        "FP"
    ],
    "viper": [
        "['vahy', 'per']",
        "FPR"
    ],
    "viral": [
        "['vahy', 'ruhl']",
        "FRL"
    ],
    "virgil": [
        "['vur', 'juhl']",
        "FRJL"
    ],
    "virgin": [
        "['vur', 'jin']",
        "FRJN"
    ],
    "virginia": [
        "[ver,jin,yuh]",
        "FRJN"
    ],
    "virginity": [
        "[ver,jin,i,tee]",
        "FRJNT"
    ],
    "virgins": [
        "[vur,jin,s]",
        "FRJNS"
    ],
    "virgo": [
        "[vur,goh]",
        "FRK"
    ],
    "virtue": [
        "[vur,choo]",
        "FRT"
    ],
    "virus": [
        "['vahy', 'ruhs']",
        "FRS"
    ],
    "visa": [
        "['vee', 'zuh']",
        "FS"
    ],
    "vision": [
        "['vizh', 'uhn']",
        "FSN"
    ],
    "vision's": [
        "[vizh,uhn,'s]",
        "FSNNS"
    ],
    "visioning": [
        "['vizh', 'uhn', 'ing']",
        "FSNNK"
    ],
    "visions": [
        "['vizh', 'uhn', 's']",
        "FSNS"
    ],
    "visit": [
        "['viz', 'it']",
        "FST"
    ],
    "visitation": [
        "[viz,i,tey,shuhn]",
        "FSTXN"
    ],
    "visiting": [
        "[viz,it,ing]",
        "FSTNK"
    ],
    "visits": [
        "[viz,it,s]",
        "FSTS"
    ],
    "visor": [
        "['vahy', 'zer']",
        "FSR"
    ],
    "visual": [
        "[vizh,oo,uhl]",
        "FSL"
    ],
    "vital": [
        "['vahyt', 'l']",
        "FTL"
    ],
    "vitals": [
        "['vahyt', 'lz']",
        "FTLS"
    ],
    "vitamin": [
        "[vahy,tuh,min]",
        "FTMN"
    ],
    "vivid": [
        "['viv', 'id']",
        "FFT"
    ],
    "vixen": [
        "[vik,suhn]",
        "FKSN"
    ],
    "vocabulary": [
        "[voh,kab,yuh,ler,ee]",
        "FKPLR"
    ],
    "vocal": [
        "['voh', 'kuhl']",
        "FKL"
    ],
    "vocals": [
        "[voh,kuhl,s]",
        "FKLS"
    ],
    "vodka": [
        "['vod', 'kuh']",
        "FTK"
    ],
    "vogue": [
        "[vohg]",
        "FK"
    ],
    "vogues": [
        "['vohg', 's']",
        "FKS"
    ],
    "voice": [
        "['vois']",
        "FS"
    ],
    "voices": [
        "['vois', 's']",
        "FSS"
    ],
    "void": [
        "[void]",
        "FT"
    ],
    "voil\u00e0": [
        "['vwah', 'lah']",
        "FL"
    ],
    "volcano": [
        "['vol', 'key', 'noh']",
        "FLKN"
    ],
    "volume": [
        "['vol', 'yoom']",
        "FLM"
    ],
    "vomit": [
        "['vom', 'it']",
        "FMT"
    ],
    "voodoo": [
        "['voo', 'doo']",
        "FT"
    ],
    "vote": [
        "['voht']",
        "FT"
    ],
    "voted": [
        "[voht,d]",
        "FTT"
    ],
    "votes": [
        "[voht,s]",
        "FTS"
    ],
    "vouch": [
        "[vouch]",
        "FX"
    ],
    "vouchers": [
        "['vou', 'cher', 's']",
        "FXRS"
    ],
    "vow": [
        "[vou]",
        "F"
    ],
    "vowel": [
        "[vou,uhl]",
        "FL"
    ],
    "vowels": [
        "['vou', 'uhl', 's']",
        "FLS"
    ],
    "vows": [
        "['vou', 's']",
        "FS"
    ],
    "vroom": [
        "['vroom']",
        "FRM"
    ],
    "vulcan": [
        "[vuhl,kuhn]",
        "FLKN"
    ],
    "vulture": [
        "['vuhl', 'cher']",
        "FLTR"
    ],
    "vultures": [
        "[vuhl,cher,s]",
        "FLTRS"
    ],
    "vv": [
        [
            "vee",
            "vee"
        ],
        "F"
    ],
    "vv's": [
        [
            "vee",
            "vees"
        ],
        "FF"
    ],
    "w": [
        "['duhb', 'uhl', 'yoo', '']",
        ""
    ],
    "wa": [
        "[waw]",
        "A"
    ],
    "wack": [
        "['wak']",
        "AK"
    ],
    "wacked": [
        "['wak', 'ed']",
        "AKT"
    ],
    "waco": [
        "[wey,koh]",
        "AK"
    ],
    "wade": [
        "['weyd']",
        "AT"
    ],
    "waffle": [
        "['wof', 'uhl']",
        "AFL"
    ],
    "waffles": [
        "[wof,uhl,s]",
        "AFLS"
    ],
    "wage": [
        "[weyj]",
        "AJ"
    ],
    "wages": [
        "[weyj,s]",
        "AJS"
    ],
    "wagon": [
        "['wag', 'uhn']",
        "AKN"
    ],
    "wagons": [
        "['wag', 'uhn', 's']",
        "AKNS"
    ],
    "waist": [
        "['weyst']",
        "AST"
    ],
    "waistline": [
        "[weyst,lahyn]",
        "ASTLN"
    ],
    "wait": [
        "['weyt']",
        "AT"
    ],
    "waited": [
        "['weyt', 'ed']",
        "ATT"
    ],
    "waiter": [
        "['wey', 'ter']",
        "ATR"
    ],
    "waiters": [
        "['wey', 'ter', 's']",
        "ATRS"
    ],
    "waiting": [
        "['wey', 'ting']",
        "ATNK"
    ],
    "waitress": [
        "['wey', 'tris']",
        "ATRS"
    ],
    "waitresses": [
        "[wey,tris,es]",
        "ATRSS"
    ],
    "waits": [
        "[weyt,s]",
        "ATS"
    ],
    "waiver": [
        "[wey,ver]",
        "AFR"
    ],
    "wake": [
        "['weyk']",
        "AK"
    ],
    "waken": [
        "[wey,kuhn]",
        "AKN"
    ],
    "wale": [
        "['weyl']",
        "AL"
    ],
    "walk": [
        "['wawk']",
        "ALK"
    ],
    "walked": [
        "['wawk', 'ed']",
        "ALKT"
    ],
    "walker": [
        "['waw', 'ker']",
        "ALKR"
    ],
    "walking": [
        "['waw', 'king']",
        "ALKNK"
    ],
    "walks": [
        "['wawk', 's']",
        "ALKS"
    ],
    "wall": [
        "['wawl']",
        "AL"
    ],
    "wallace": [
        "['wol', 'is']",
        "ALS"
    ],
    "wallet": [
        "['wol', 'it']",
        "ALT"
    ],
    "wallets": [
        "['wol', 'it', 's']",
        "ALTS"
    ],
    "walls": [
        "['wawl', 's']",
        "ALS"
    ],
    "wally": [
        "[wey,lee]",
        "AL"
    ],
    "walnuts": [
        "[wawl,nuht,s]",
        "ALNTS"
    ],
    "walter": [
        "[vahl,terfor1]",
        "ALTR"
    ],
    "wan": [
        "['won']",
        "AN"
    ],
    "wander": [
        "[won,der]",
        "ANTR"
    ],
    "wandering": [
        "[won,der,ing]",
        "ANTRNK"
    ],
    "wannabe": [
        "['won', 'uh', 'bee']",
        "ANP"
    ],
    "wanner": [
        "['won', 'ner']",
        "ANR"
    ],
    "want": [
        "['wont']",
        "ANT"
    ],
    "wanted": [
        "['wont', 'ed']",
        "ANTT"
    ],
    "wanting": [
        "['won', 'ting']",
        "ANTNK"
    ],
    "wants": [
        "['wont', 's']",
        "ANTS"
    ],
    "war": [
        "['wawr']",
        "AR"
    ],
    "war's": [
        "[wawr,'s]",
        "ARRS"
    ],
    "ward": [
        "['wawrd']",
        "ART"
    ],
    "warden": [
        "['wawr', 'dn']",
        "ARTN"
    ],
    "wardrobe": [
        "['wawr', 'drohb']",
        "ARTRP"
    ],
    "ware": [
        "[wair]",
        "AR"
    ],
    "warfare": [
        "['wawr', 'fair']",
        "ARFR"
    ],
    "warhol": [
        "[wawr,hawl]",
        "ARL"
    ],
    "warm": [
        "['wawrm']",
        "ARM"
    ],
    "warmer": [
        "[wawrm,er]",
        "ARMR"
    ],
    "warming": [
        "[wawrm,ing]",
        "ARMNK"
    ],
    "warmth": [
        "[wawrmth]",
        "ARM0"
    ],
    "warn": [
        "[wawrn]",
        "ARN"
    ],
    "warned": [
        "['wawrn', 'ed']",
        "ARNT"
    ],
    "warner": [
        "['wawr', 'ner']",
        "ARNR"
    ],
    "warning": [
        "['wawr', 'ning']",
        "ARNNK"
    ],
    "warrant": [
        "['wawr', 'uhnt']",
        "ARNT"
    ],
    "warrants": [
        "['wawr', 'uhnt', 's']",
        "ARNTS"
    ],
    "warren": [
        "['wawr', 'uhn']",
        "ARN"
    ],
    "warring": [
        "[wawr,ring]",
        "ARNK"
    ],
    "warrior": [
        "['wawr', 'ee', 'er']",
        "ARR"
    ],
    "warriors": [
        "[wawr,ee,er,s]",
        "ARRS"
    ],
    "wars": [
        "['wawr', 's']",
        "ARS"
    ],
    "was": [
        "['wuhz']",
        "AS"
    ],
    "wasabi": [
        "['wah', 'suh', 'bee']",
        "ASP"
    ],
    "wash": [
        "['wosh']",
        "AX"
    ],
    "washed": [
        "['wosh', 'ed']",
        "AXT"
    ],
    "washer": [
        "['wosh', 'er']",
        "AXR"
    ],
    "washes": [
        "[wosh,es]",
        "AXS"
    ],
    "washing": [
        "['wosh', 'ing']",
        "AXNK"
    ],
    "washington": [
        "[wosh,ing,tuhn]",
        "AXNKTN"
    ],
    "washingtons": [
        "['wosh', 'ing', 'tuhn', 's']",
        "AXNKTNS"
    ],
    "washy": [
        "['wosh', 'ee']",
        "AX"
    ],
    "wasn't": [
        "['wuhz', 'uhnt']",
        "ASNNT"
    ],
    "wasp": [
        "[wosp]",
        "ASP"
    ],
    "wassup": [
        "['wuhs', 'uhp']",
        "ASP"
    ],
    "waste": [
        "['weyst']",
        "AST"
    ],
    "wasted": [
        "['wey', 'stid']",
        "ASTT"
    ],
    "wasting": [
        "['wey', 'sting']",
        "ASTNK"
    ],
    "watch": [
        "['woch']",
        "AX"
    ],
    "watched": [
        "['woch', 'ed']",
        "AXT"
    ],
    "watchers": [
        "[woch,er,s]",
        "AXRS"
    ],
    "watches": [
        "['woch', 'es']",
        "AXS"
    ],
    "watching": [
        "['woch', 'ing']",
        "AXNK"
    ],
    "water": [
        "['waw', 'ter']",
        "ATR"
    ],
    "water's": [
        "[waw,ter,'s]",
        "ATRRS"
    ],
    "watered": [
        "['waw', 'terd']",
        "ATRT"
    ],
    "waterfall": [
        "['waw', 'ter', 'fawl']",
        "ATRFL"
    ],
    "waters": [
        "['waw', 'terz']",
        "ATRS"
    ],
    "watery": [
        "[waw,tuh,ree]",
        "ATR"
    ],
    "wats": [
        "[wots]",
        "ATS"
    ],
    "watson": [
        "[wot,suhn]",
        "ATSN"
    ],
    "watts": [
        "['wots']",
        "ATS"
    ],
    "wave": [
        "['weyv']",
        "AF"
    ],
    "waved": [
        "['weyvd']",
        "AFT"
    ],
    "waves": [
        "['weyvz']",
        "AFS"
    ],
    "wavy": [
        "['wey', 'vee']",
        "AF"
    ],
    "wax": [
        "['waks']",
        "AKS"
    ],
    "way": [
        "['wey']",
        "A"
    ],
    "wayne": [
        "['weyn']",
        "AN"
    ],
    "wayne's": [
        "['weyn', \"'s\"]",
        "ANS"
    ],
    "waynes": [
        "['weyn', 's']",
        "ANS"
    ],
    "ways": [
        "['weyz']",
        "AS"
    ],
    "we": [
        "['wee']",
        "A"
    ],
    "we'd": [
        "['weed']",
        "AT"
    ],
    "we'll": [
        "['weel']",
        "AL"
    ],
    "we're": [
        "['weer']",
        "AR"
    ],
    "we've": [
        "['weev']",
        "AF"
    ],
    "weak": [
        "['week']",
        "AK"
    ],
    "weaker": [
        "[week,er]",
        "AKR"
    ],
    "weakness": [
        "['week', 'nis']",
        "AKNS"
    ],
    "wealth": [
        "['welth']",
        "AL0"
    ],
    "wealthy": [
        "[wel,thee]",
        "AL0"
    ],
    "weapon": [
        "['wep', 'uhn']",
        "APN"
    ],
    "weaponry": [
        "[wep,uhn,ree]",
        "APNR"
    ],
    "weapons": [
        "[wep,uhn,s]",
        "APNS"
    ],
    "wear": [
        "['wair']",
        "AR"
    ],
    "wearing": [
        "['wair', 'ing']",
        "ARNK"
    ],
    "wears": [
        "[wair,s]",
        "ARS"
    ],
    "weasel": [
        "[wee,zuhl]",
        "ASL"
    ],
    "weather": [
        "['weth', 'er']",
        "A0R"
    ],
    "weave": [
        "['weev']",
        "AF"
    ],
    "weaves": [
        "['weev', 's']",
        "AFS"
    ],
    "web": [
        "['web']",
        "AP"
    ],
    "webb": [
        "[web]",
        "AP"
    ],
    "website": [
        "[web,sahyt]",
        "APST"
    ],
    "wedding": [
        "['wed', 'ing']",
        "ATNK"
    ],
    "wednesday": [
        "['wenz', 'dey']",
        "ATNST"
    ],
    "wednesdays": [
        "[wenz,deyz]",
        "ATNSTS"
    ],
    "wee": [
        "['wee']",
        "A"
    ],
    "weed": [
        "['weed']",
        "AT"
    ],
    "weed's": [
        "[weed,'s]",
        "ATTS"
    ],
    "week": [
        "['week']",
        "AK"
    ],
    "weekday": [
        "['week', 'dey']",
        "AKT"
    ],
    "weekend": [
        "['week', 'end']",
        "AKNT"
    ],
    "weekends": [
        "['week', 'endz']",
        "AKNTS"
    ],
    "weeks": [
        "['week', 's']",
        "AKS"
    ],
    "weep": [
        "['weep']",
        "AP"
    ],
    "weigh": [
        "['wey']",
        "A"
    ],
    "weighed": [
        "[wey,ed]",
        "AT"
    ],
    "weighing": [
        "['wey', 'ing']",
        "ANK"
    ],
    "weighs": [
        "['wey', 's']",
        "AS"
    ],
    "weight": [
        "['weyt']",
        "AT"
    ],
    "weights": [
        "[weyt,s]",
        "ATS"
    ],
    "weird": [
        "['weerd']",
        "ART"
    ],
    "weirdo": [
        "['weer', 'doh']",
        "ART"
    ],
    "weirdos": [
        "[weer,doh,s]",
        "ARTS"
    ],
    "welcome": [
        "['wel', 'kuhm']",
        "ALKM"
    ],
    "welfare": [
        "[wel,fair]",
        "ALFR"
    ],
    "well": [
        "['wel']",
        "AL"
    ],
    "wells": [
        "[welz]",
        "ALS"
    ],
    "wen": [
        "['wen']",
        "AN"
    ],
    "wendy": [
        "['wen', 'dee']",
        "ANT"
    ],
    "went": [
        "['went']",
        "ANT"
    ],
    "wept": [
        "[wept]",
        "APT"
    ],
    "were": [
        "['wur']",
        "AR"
    ],
    "weren't": [
        "['wurnt']",
        "ARNNT"
    ],
    "wesley": [
        "[wes,lee]",
        "ASL"
    ],
    "west": [
        "['west']",
        "AST"
    ],
    "western": [
        "['wes', 'tern']",
        "ASTRN"
    ],
    "weston": [
        "[wes,tuhn]",
        "ASTN"
    ],
    "westside": [
        [
            "west",
            "sahyd"
        ],
        "ASTST"
    ],
    "wet": [
        "['wet']",
        "AT"
    ],
    "wetted": [
        "[wet,ted]",
        "ATT"
    ],
    "wetter": [
        "['wet', 'ter']",
        "ATR"
    ],
    "wetting": [
        "['wet', 'ting']",
        "ATNK"
    ],
    "whack": [
        "['hwak']",
        "AK"
    ],
    "whacked": [
        "['hwakt']",
        "AKT"
    ],
    "whale": [
        "['hweyl']",
        "AL"
    ],
    "wham": [
        "['hwam']",
        "AM"
    ],
    "what": [
        "['hwuht']",
        "AT"
    ],
    "what's": [
        "['hwuhts']",
        "ATTS"
    ],
    "whatchamacallit": [
        "[hwuhch,uh,muh,kawl,it]",
        "AXMKLT"
    ],
    "whatever": [
        "['hwuht', 'ev', 'er']",
        "ATFR"
    ],
    "whatever's": [
        [
            "hwuht",
            "ev",
            "ers"
        ],
        "ATFRRS"
    ],
    "wheel": [
        "['hweel']",
        "AL"
    ],
    "wheelchair": [
        "[hweel,chair]",
        "ALXR"
    ],
    "wheeler": [
        "[hwee,ler]",
        "ALR"
    ],
    "wheelers": [
        "['hwee', 'ler', 's']",
        "ALRS"
    ],
    "wheelie": [
        "['hwee', 'lee']",
        "AL"
    ],
    "wheeling": [
        "['hwee', 'ling']",
        "ALNK"
    ],
    "wheels": [
        "['hweel', 's']",
        "ALS"
    ],
    "wheezy": [
        "['hwee', 'zee']",
        "AS"
    ],
    "when": [
        "['hwen']",
        "AN"
    ],
    "when's": [
        "['hwenz']",
        "ANNS"
    ],
    "whenever": [
        "['hwen', 'ev', 'er']",
        "ANFR"
    ],
    "where": [
        "['hwair']",
        "AR"
    ],
    "where's": [
        "['hwairz']",
        "ARS"
    ],
    "wherever": [
        "['hwair', 'ev', 'er']",
        "ARFR"
    ],
    "whether": [
        "['hweth', 'er']",
        "A0R"
    ],
    "whew": [
        "['hwyoo']",
        "A"
    ],
    "which": [
        "['hwich']",
        "AX"
    ],
    "whichever": [
        "['hwich', 'ev', 'er']",
        "AXFR"
    ],
    "while": [
        "['hwahyl']",
        "AL"
    ],
    "whine": [
        "['hwahyn']",
        "AN"
    ],
    "whined": [
        "[hwahyn,d]",
        "ANT"
    ],
    "whining": [
        [
            "hwahyn",
            "ing"
        ],
        "ANNK"
    ],
    "whip": [
        "['hwip']",
        "AP"
    ],
    "whipped": [
        "['hwipt']",
        "APT"
    ],
    "whipping": [
        "['hwip', 'ing']",
        "APNK"
    ],
    "whipping's": [
        "[hwip,ing,'s]",
        "APNKKS"
    ],
    "whips": [
        "['hwip', 's']",
        "APS"
    ],
    "whirlwind": [
        "[hwurl,wind]",
        "ARLNT"
    ],
    "whiskers": [
        "['hwis', 'ker', 's']",
        "ASKRS"
    ],
    "whiskey": [
        "['hwis', 'kee']",
        "ASK"
    ],
    "whisky": [
        "[hwis,kee]",
        "ASK"
    ],
    "whisper": [
        "[hwis,per]",
        "ASPR"
    ],
    "whispered": [
        "['hwis', 'perd']",
        "ASPRT"
    ],
    "whispering": [
        "[hwis,per,ing]",
        "ASPRNK"
    ],
    "whispers": [
        "[hwis,per,s]",
        "ASPRS"
    ],
    "whistle": [
        "['hwis', 'uhl']",
        "ASTL"
    ],
    "whistling": [
        "[hwis,ling]",
        "ASTLNK"
    ],
    "white": [
        "['hwahyt']",
        "AT"
    ],
    "whiter": [
        "['hwahyt', 'r']",
        "ATR"
    ],
    "whites": [
        "['hwahyt', 's']",
        "ATS"
    ],
    "whitest": [
        "[hwahyt,st]",
        "ATST"
    ],
    "whitey": [
        "[hwahy,tee]",
        "AT"
    ],
    "whitney": [
        "['hwit', 'nee']",
        "ATN"
    ],
    "who": [
        "['hoo']",
        "A"
    ],
    "who's": [
        "['hooz']",
        "AS"
    ],
    "whoa": [
        "['hwoh']",
        "A"
    ],
    "whoever": [
        "['hoo', 'ev', 'er']",
        "AFR"
    ],
    "whole": [
        "['hohl']",
        "AL"
    ],
    "wholesome": [
        "[hohl,suhm]",
        "ALSM"
    ],
    "whoop": [
        "['hoop']",
        "AP"
    ],
    "whooping": [
        "[hoop,ing]",
        "APNK"
    ],
    "whopper": [
        "['hwop', 'er']",
        "APR"
    ],
    "whore": [
        "['hawr']",
        "AR"
    ],
    "whores": [
        "['hawr', 's']",
        "ARS"
    ],
    "whos": [
        [
            "hoos"
        ],
        "AS"
    ],
    "whose": [
        "['hooz']",
        "AS"
    ],
    "why": [
        "['hwahy']",
        "A"
    ],
    "why's": [
        "[hwahyz]",
        "AS"
    ],
    "whys": [
        "[hwahy,s]",
        "AS"
    ],
    "wi": [
        [
            "wee"
        ],
        "A"
    ],
    "wick": [
        "['wik']",
        "AK"
    ],
    "wicked": [
        "['wik', 'id']",
        "AKT"
    ],
    "wickedness": [
        "[wik,id,nis]",
        "AKTNS"
    ],
    "wide": [
        "['wahyd']",
        "AT"
    ],
    "widow": [
        "['wid', 'oh']",
        "AT"
    ],
    "wieners": [
        "[wee,ner,s]",
        "ANRS"
    ],
    "wife": [
        "['wahyf']",
        "AF"
    ],
    "wig": [
        "['wig']",
        "AK"
    ],
    "wiggle": [
        "[wig,uhl]",
        "AKL"
    ],
    "wigs": [
        "[wig,s]",
        "AKS"
    ],
    "wild": [
        "['wahyld']",
        "ALT"
    ],
    "wilder": [
        "['wil', 'der']",
        "ALTR"
    ],
    "wildest": [
        "['wahyld', 'est']",
        "ALTST"
    ],
    "wilding": [
        "['wahyl', 'ding']",
        "ALTNK"
    ],
    "wile": [
        "[wahyl]",
        "AL"
    ],
    "will": [
        "['wil']",
        "AL"
    ],
    "williams": [
        "['wil', 'yuhmz']",
        "ALMS"
    ],
    "willie": [
        "['wil', 'ee']",
        "AL"
    ],
    "willies": [
        "[wil,eez]",
        "ALS"
    ],
    "willing": [
        "['wil', 'ing']",
        "ALNK"
    ],
    "willis": [
        "['wil', 'is']",
        "ALS"
    ],
    "wills": [
        "[wilz]",
        "ALS"
    ],
    "wilt": [
        "['wilt']",
        "ALT"
    ],
    "wimp": [
        "[wimp]",
        "AMP"
    ],
    "wind": [
        "['nounwind']",
        "ANT"
    ],
    "winding": [
        "['wahyn', 'ding']",
        "ANTNK"
    ],
    "window": [
        "['win', 'doh']",
        "ANT"
    ],
    "windows": [
        "['win', 'dohz']",
        "ANTS"
    ],
    "winds": [
        "['nounwind', 's']",
        "ANTS"
    ],
    "windshield": [
        "[wind,sheeld]",
        "ANTXLT"
    ],
    "windy": [
        "['win', 'dee']",
        "ANT"
    ],
    "wine": [
        "['wahyn']",
        "AN"
    ],
    "wines": [
        "[wahyn,s]",
        "ANS"
    ],
    "wing": [
        "['wing']",
        "ANK"
    ],
    "wings": [
        "['wingz']",
        "ANKS"
    ],
    "wink": [
        "['wingk']",
        "ANK"
    ],
    "winked": [
        "[wingk,ed]",
        "ANKT"
    ],
    "winnebago": [
        "['win', 'uh', 'bey', 'goh']",
        "ANPK"
    ],
    "winner": [
        "['win', 'er']",
        "ANR"
    ],
    "winners": [
        "['win', 'er', 's']",
        "ANRS"
    ],
    "winning": [
        "['win', 'ing']",
        "ANNK"
    ],
    "wins": [
        "[win,s]",
        "ANS"
    ],
    "winslow": [
        "[winz,loh]",
        "ANSL"
    ],
    "winter": [
        "['win', 'ter']",
        "ANTR"
    ],
    "winter's": [
        "['win', 'ter', \"'s\"]",
        "ANTRRS"
    ],
    "winters": [
        "[win,terz]",
        "ANTRS"
    ],
    "wintertime": [
        "['win', 'ter', 'tahym']",
        "ANTRTM"
    ],
    "wipe": [
        "['wahyp']",
        "AP"
    ],
    "wiped": [
        "['wahyp', 'd']",
        "APT"
    ],
    "wipes": [
        "[wahyp,s]",
        "APS"
    ],
    "wire": [
        "['wahyuhr']",
        "AR"
    ],
    "wired": [
        "['wahyuhrd']",
        "ART"
    ],
    "wires": [
        "['wahyuhr', 's']",
        "ARS"
    ],
    "wis": [
        "['wis']",
        "AS"
    ],
    "wisdom": [
        "['wiz', 'duhm']",
        "ASTM"
    ],
    "wise": [
        "['wahyz']",
        "AS"
    ],
    "wisely": [
        "['wahyz', 'ly']",
        "ASL"
    ],
    "wiser": [
        "['wahyz', 'r']",
        "ASR"
    ],
    "wish": [
        "['wish']",
        "AX"
    ],
    "wished": [
        "['wish', 'ed']",
        "AXT"
    ],
    "wishes": [
        "['wish', 'es']",
        "AXS"
    ],
    "wishing": [
        "['wish', 'ing']",
        "AXNK"
    ],
    "wit": [
        "['wit']",
        "AT"
    ],
    "witch": [
        "['wich']",
        "AX"
    ],
    "witches": [
        "[wich,es]",
        "AXS"
    ],
    "with": [
        "['with']",
        "A0"
    ],
    "withdrawals": [
        "[with,draw,uhl,s]",
        "A0TRLS"
    ],
    "within": [
        "['with', 'in']",
        "A0N"
    ],
    "without": [
        "['with', 'out']",
        "A0T"
    ],
    "witness": [
        "['wit', 'nis']",
        "ATNS"
    ],
    "witnessed": [
        "['wit', 'nis', 'ed']",
        "ATNST"
    ],
    "witnesses": [
        "['wit', 'nis', 'es']",
        "ATNSS"
    ],
    "wits": [
        "[wit,s]",
        "ATS"
    ],
    "witty": [
        "[wit,ee]",
        "AT"
    ],
    "wives": [
        "[wahyvz]",
        "AFS"
    ],
    "wizard": [
        "['wiz', 'erd']",
        "ASRT"
    ],
    "woah": [
        [
            "woh",
            "ah"
        ],
        "A"
    ],
    "wobble": [
        "['wob', 'uhl']",
        "APL"
    ],
    "wobbling": [
        "[wob,ling]",
        "APLNK"
    ],
    "wobbly": [
        "[wob,lee]",
        "APL"
    ],
    "woe": [
        "[woh]",
        "A"
    ],
    "woes": [
        "['woh', 's']",
        "AS"
    ],
    "woke": [
        "['wohk']",
        "AK"
    ],
    "wolf": [
        "['woolf']",
        "ALF"
    ],
    "wolverine": [
        "[wool,vuh,reen]",
        "ALFRN"
    ],
    "wolves": [
        "['woolvz']",
        "ALFS"
    ],
    "woman": [
        "['woom', 'uhn']",
        "AMN"
    ],
    "woman's": [
        "[woom,uhn,'s]",
        "AMNNS"
    ],
    "womb": [
        "[woom]",
        "AMP"
    ],
    "women": [
        "['wim', 'in']",
        "AMN"
    ],
    "won": [
        "['wuhn']",
        "AN"
    ],
    "won't": [
        "['wohnt']",
        "ANNT"
    ],
    "wonder": [
        "['wuhn', 'der']",
        "ANTR"
    ],
    "wondered": [
        "[wuhn,der,ed]",
        "ANTRT"
    ],
    "wonderful": [
        "['wuhn', 'der', 'fuhl']",
        "ANTRFL"
    ],
    "wondering": [
        "['wuhn', 'der', 'ing']",
        "ANTRNK"
    ],
    "wonders": [
        "[wuhn,der,s]",
        "ANTRS"
    ],
    "wont": [
        "['wawnt']",
        "ANT"
    ],
    "woo": [
        "['woo']",
        "A"
    ],
    "wood": [
        "['wood']",
        "AT"
    ],
    "wooden": [
        "[wood,n]",
        "ATN"
    ],
    "woodgrain": [
        "[wood,greyn]",
        "ATKRN"
    ],
    "woods": [
        "['woodz']",
        "ATS"
    ],
    "woody": [
        "['wood', 'ee']",
        "AT"
    ],
    "woof": [
        "['woof']",
        "AF"
    ],
    "woofers": [
        "[woof,er,s]",
        "AFRS"
    ],
    "wool": [
        "['wool']",
        "AL"
    ],
    "wooly": [
        "['wool', 'ee']",
        "AL"
    ],
    "woozy": [
        "[woo,zee]",
        "AS"
    ],
    "wop": [
        "['wop']",
        "AP"
    ],
    "wops": [
        "['wop', 's']",
        "APS"
    ],
    "word": [
        "['wurd']",
        "ART"
    ],
    "wordplay": [
        "['wurd', 'pley']",
        "ARTPL"
    ],
    "words": [
        "['wurd', 's']",
        "ARTS"
    ],
    "wore": [
        "['wawr']",
        "AR"
    ],
    "work": [
        "['wurk']",
        "ARK"
    ],
    "worked": [
        "['wurkt']",
        "ARKT"
    ],
    "worker": [
        "['wur', 'ker']",
        "ARKR"
    ],
    "workers": [
        "['wur', 'ker', 's']",
        "ARKRS"
    ],
    "working": [
        "['wur', 'king']",
        "ARKNK"
    ],
    "workout": [
        "['wurk', 'out']",
        "ARKT"
    ],
    "workplace": [
        "['wurk', 'pleys']",
        "ARKPLS"
    ],
    "works": [
        "['wurk', 's']",
        "ARKS"
    ],
    "world": [
        "['wurld']",
        "ARLT"
    ],
    "world's": [
        "['wurld', \"'s\"]",
        "ARLTTS"
    ],
    "worlds": [
        "[wurld,s]",
        "ARLTS"
    ],
    "worldwide": [
        "['wurld', 'wahyd']",
        "ARLTT"
    ],
    "worm": [
        "[wurm]",
        "ARM"
    ],
    "worms": [
        "[wurmz]",
        "ARMS"
    ],
    "worn": [
        "[wawrn]",
        "ARN"
    ],
    "worried": [
        "['wur', 'eed']",
        "ART"
    ],
    "worry": [
        "['wur', 'ee']",
        "AR"
    ],
    "worrying": [
        "['wur', 'ee', 'ing']",
        "ARNK"
    ],
    "worse": [
        "['wurs']",
        "ARS"
    ],
    "worser": [
        "[wur,ser]",
        "ARSR"
    ],
    "worship": [
        "['wur', 'ship']",
        "ARXP"
    ],
    "worst": [
        "['wurst']",
        "ARST"
    ],
    "worth": [
        "['wurth']",
        "AR0"
    ],
    "worthless": [
        "['wurth', 'lis']",
        "AR0LS"
    ],
    "worthy": [
        "['wur', 'thee']",
        "AR0"
    ],
    "would": [
        "['wood']",
        "ALT"
    ],
    "would've": [
        [
            "wood",
            "ahv"
        ],
        "ALTTF"
    ],
    "woulda": [
        [
            "wood",
            "ah"
        ],
        "ALT"
    ],
    "wouldn't": [
        "['wood', 'nt']",
        "ALTNNT"
    ],
    "wound": [
        "['woond']",
        "ANT"
    ],
    "wounds": [
        "['woond', 's']",
        "ANTS"
    ],
    "wow": [
        "['wou']",
        "A"
    ],
    "wow's": [
        "[wou,'s]",
        "AS"
    ],
    "wraith": [
        "['reyth']",
        "R0"
    ],
    "wrap": [
        "['rap']",
        "RP"
    ],
    "wrapped": [
        "['rap', 'ped']",
        "RPT"
    ],
    "wrapper": [
        "['rap', 'er']",
        "RPR"
    ],
    "wrappers": [
        "[rap,er,s]",
        "RPRS"
    ],
    "wrapping": [
        "['rap', 'ing']",
        "RPNK"
    ],
    "wraps": [
        "[rap,s]",
        "RPS"
    ],
    "wrath": [
        "[rath]",
        "R0"
    ],
    "wreck": [
        "['rek']",
        "RK"
    ],
    "wrecked": [
        "['rek', 'ed']",
        "RKT"
    ],
    "wrecking": [
        "[rek,ing]",
        "RKNK"
    ],
    "wrestle": [
        "['res', 'uhl']",
        "RSTL"
    ],
    "wrestler": [
        "['res', 'uhl', 'r']",
        "RSTLR"
    ],
    "wrestling": [
        "[res,ling]",
        "RSTLNK"
    ],
    "wright": [
        "['rahyt']",
        "RT"
    ],
    "wrinkle": [
        "[ring,kuhl]",
        "RNKL"
    ],
    "wrinkles": [
        "[ring,kuhl,s]",
        "RNKLS"
    ],
    "wrist": [
        "['rist']",
        "RST"
    ],
    "wristband": [
        "[rist,band]",
        "RSTPNT"
    ],
    "wrists": [
        "['rist', 's']",
        "RSTS"
    ],
    "write": [
        "['rahyt']",
        "RT"
    ],
    "writer": [
        "['rahy', 'ter']",
        "RTR"
    ],
    "writers": [
        "[rahy,ter,s]",
        "RTRS"
    ],
    "writing": [
        "['rahy', 'ting']",
        "RTNK"
    ],
    "written": [
        "[rit,n]",
        "RTN"
    ],
    "wrong": [
        "['rawng']",
        "RNK"
    ],
    "wrongs": [
        "['rawng', 's']",
        "RNKS"
    ],
    "wrote": [
        "['roht']",
        "RT"
    ],
    "wu": [
        "['woo']",
        "A"
    ],
    "wus": [
        "[woo,s]",
        "AS"
    ],
    "x": [
        "['eks', '']",
        "S"
    ],
    "xanax": [
        "['zan', 'aks']",
        "SNKS"
    ],
    "y": [
        "['wahy', '']",
        "A"
    ],
    "y'all": [
        "['yawl']",
        "AAL"
    ],
    "ya'll": [
        [
            "yawl"
        ],
        "AL"
    ],
    "yacht": [
        "['yot']",
        "AKT"
    ],
    "yachts": [
        "[yot,s]",
        "AKTS"
    ],
    "yack": [
        "[yak]",
        "AK"
    ],
    "yak": [
        "[yak]",
        "AK"
    ],
    "yam": [
        "['yam']",
        "AM"
    ],
    "yams": [
        "['yam', 's']",
        "AMS"
    ],
    "yang": [
        "[yahng]",
        "ANK"
    ],
    "yankee": [
        "['yang', 'kee']",
        "ANK"
    ],
    "yankees": [
        "[yang,kee,s]",
        "ANKS"
    ],
    "yap": [
        "[yap]",
        "AP"
    ],
    "yapping": [
        "['yap', 'ping']",
        "APNK"
    ],
    "yard": [
        "['yahrd']",
        "ART"
    ],
    "yards": [
        "[yahrd,s]",
        "ARTS"
    ],
    "yawn": [
        "['yawn']",
        "AN"
    ],
    "yawning": [
        "['yaw', 'ning']",
        "ANNK"
    ],
    "yay": [
        "['yey']",
        "A"
    ],
    "ye": [
        "['yee']",
        "A"
    ],
    "yeah": [
        "['yai']",
        "A"
    ],
    "year": [
        "['yeer']",
        "AR"
    ],
    "year's": [
        "[yeer,'s]",
        "ARRS"
    ],
    "years": [
        "['yeer', 's']",
        "ARS"
    ],
    "yeast": [
        "[yeest]",
        "AST"
    ],
    "yell": [
        "['yel']",
        "AL"
    ],
    "yelled": [
        "[yel,ed]",
        "ALT"
    ],
    "yeller": [
        [
            "yel",
            "er"
        ],
        "ALR"
    ],
    "yelling": [
        "['yel', 'ing']",
        "ALNK"
    ],
    "yellow": [
        "['yel', 'oh']",
        "AL"
    ],
    "yells": [
        "[yel,s]",
        "ALS"
    ],
    "yen": [
        "['yen']",
        "AN"
    ],
    "yep": [
        "['yep']",
        "AP"
    ],
    "yes": [
        "['yes']",
        "AS"
    ],
    "yesterday": [
        "['yes', 'ter', 'dey']",
        "ASTRT"
    ],
    "yet": [
        "['yet']",
        "AT"
    ],
    "yi": [
        "[yee]",
        "A"
    ],
    "yin": [
        "[yin]",
        "AN"
    ],
    "yo": [
        "['yoh']",
        "A"
    ],
    "yoda": [
        [
            "yoh",
            "duh"
        ],
        "AT"
    ],
    "yoga": [
        "['yoh', 'guh']",
        "AK"
    ],
    "yogi": [
        "[yoh,gee]",
        "AJ"
    ],
    "yolk": [
        "[yohk]",
        "ALK"
    ],
    "york": [
        "['yawrk']",
        "ARK"
    ],
    "york's": [
        "[yawrk,'s]",
        "ARKKS"
    ],
    "yosemite": [
        "[yoh,sem,i,tee]",
        "ASMT"
    ],
    "you": [
        "['yoo']",
        "A"
    ],
    "you'd": [
        "['yood']",
        "AT"
    ],
    "you'll": [
        "['yool']",
        "AL"
    ],
    "you're": [
        "['yoor']",
        "AR"
    ],
    "you's": [
        "['yoo', \"'s\"]",
        "AS"
    ],
    "you've": [
        "['yoov']",
        "AF"
    ],
    "young": [
        "['yuhng']",
        "ANK"
    ],
    "younger": [
        "['yuhng', 'ger']",
        "ANKR"
    ],
    "youngest": [
        "['yuhng', 'gist']",
        "ANJST"
    ],
    "youngins": [
        [
            "yuhng",
            "ins"
        ],
        "ANJNS"
    ],
    "your": [
        "['yoor']",
        "AR"
    ],
    "yours": [
        "['yoorz']",
        "ARS"
    ],
    "yourself": [
        "['yoor', 'self']",
        "ARSLF"
    ],
    "youth": [
        "[yooth]",
        "A0"
    ],
    "yuck": [
        "['yuhk']",
        "AK"
    ],
    "yummy": [
        "[yuhm,ee]",
        "AM"
    ],
    "yup": [
        "['yuhp']",
        "AP"
    ],
    "zag": [
        "['zag']",
        "SK"
    ],
    "zags": [
        "['zag', 's']",
        "SKS"
    ],
    "zebra": [
        "['zee', 'bruh']",
        "SPR"
    ],
    "zero": [
        "['zeer', 'oh']",
        "SR"
    ],
    "zeroes": [
        "['zeer', 'oh', 'es']",
        "SRS"
    ],
    "zeros": [
        "['zeer', 'oh', 's']",
        "SRS"
    ],
    "zig": [
        "['zig']",
        "SK"
    ],
    "zillion": [
        "[zil,yuhn]",
        "SLN"
    ],
    "zion": [
        "[zahy,uhn]",
        "SN"
    ],
    "zip": [
        "['zip']",
        "SP"
    ],
    "ziploc": [
        "['zip', 'lok']",
        "SPLK"
    ],
    "zipped": [
        "['zip', 'ped']",
        "SPT"
    ],
    "zipper": [
        "['zip', 'er']",
        "SPR"
    ],
    "zippers": [
        "['zip', 'er', 's']",
        "SPRS"
    ],
    "zipping": [
        "[zip,ping]",
        "SPNK"
    ],
    "zit": [
        "[zit]",
        "ST"
    ],
    "zombie": [
        "['zom', 'bee']",
        "SMP"
    ],
    "zombies": [
        "[zom,bee,s]",
        "SMPS"
    ],
    "zone": [
        "['zohn']",
        "SN"
    ],
    "zones": [
        "['zohn', 's']",
        "SNS"
    ],
    "zoning": [
        "['zoh', 'ning']",
        "SNNK"
    ],
    "zoo": [
        "['zoo']",
        "S"
    ],
    "zoom": [
        "['zoom']",
        "SM"
    ],
    "zooming": [
        "[zoom,ing]",
        "SMNK"
    ],
    "zulu": [
        "['zoo', 'loo']",
        "SL"
    ]
    }
    return corpus