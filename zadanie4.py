import math
import random
import matplotlib.pyplot as plt
import copy
import time




min_position = -5000
max_position = 5000
OFFSET = 100


class Point:        # trieda pre reprezentaciu bodov
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.color = 0
        self.distance_centroid = 0
        self.distance_medoid = 0

""" GENEROVANIE """
def is_unique(a,b,number):  #funkcia na overenie, ci su vsetky body jedinecne

    found_duplicate = False
    while(True):
        new_points = generate_base(a, b, number)
        for i in new_points:
            if new_points.count(i) > 1:
                found_duplicate = True
        if(found_duplicate == False):
            break
    return new_points

def create_base_point(a,b): # vytvor zakladny bod bez OFFSETu
    x = random.randrange(a,b)
    y = random.randrange(a,b)
    centroid = Point(x,y)
    return centroid

def generate_base(a,b,number):
    centroids = []
    for i in range(0,number,1):
        centroids.append(create_base_point(a,b))
        centroids[i].color = i
    return centroids

def create_new_point(father):   # generovanie bodov s OFFSETom
    new_x = random.gauss(father.x, OFFSET)
    if(new_x <= -5000):
        new_x = -5000
    elif(new_x >= 5000):
        new_x = 5000


    new_y = random.gauss(father.y, OFFSET)
    if (new_y <= -5000):
        new_y = -5000
    elif (new_y >= 5000):
        new_y = 5000

    new_point = Point(new_x, new_y)
    return new_point

def generate_points(centroids, number):     # vygeneruje vsetky body
    temp_points = centroids.copy()

    for i in range(number):
        father = random.choice(temp_points)
        temp_points.append(create_new_point(father))

    return temp_points[CLUSTERS:]

"""     POMOCNE FUNCKIE     """

def distance(p1, p2):   # vypocitanie vzdialenosi euklid
    x = abs(p1.x - p2.x)
    y = abs(p1.y - p2.y)
    result = math.sqrt(x**2 + y**2)

    return result

def calculate_middle_of_clusters(num_of_cluster, points):   # funkcia na vypocitanie stredu klastra/ centroidu
    sums_x = []
    sums_y = []
    nums = []
    stredy =[]
    for i in range(num_of_cluster):
        sums_x.append(0)
        sums_y.append(0)
        nums.append(0)

    for point in points:    # vypocitam sumy a pocty bodov v clustery
        sums_x[point.color] += point.x
        sums_y[point.color] += point.y
        nums[point.color] += 1

    for i in range(num_of_cluster):
        a = Point(sums_x[i]/nums[i],sums_y[i]/nums[i])
        a.color = i
        stredy.append(a)

    return stredy

def recalculate_centroids(centroids, points):   # prepocita suradnice centroidov ak nastala zmena v klastroch
    sums_x = [0]*len(centroids)
    sums_y = [0]*len(centroids)
    nums = [0]*len(centroids)


    for point in points:    # vypocitam sumy a pocty bodov v clustery
        sums_x[point.color] += point.x
        sums_y[point.color] += point.y
        nums[point.color] += 1

    nastala_zmena = False
    for i in range(0, len(centroids), 1):   # pre kazdy centroid vypocitam novu poziciu
        if(nums[i] > 0):
            start_x = centroids[i].x
            start_y = centroids[i].y
            new_x = sums_x[i] / nums[i]
            new_y = sums_y[i] / nums[i]
            if(start_x != new_x or start_y != new_y ):
                centroids[i].x = new_x
                centroids[i].y = new_y
                nastala_zmena = True

    return nastala_zmena

def assign_points_to_closest(centroids, points):  # toto vlastne iba porovna point so vsetkymi centroidmi/medoidmi a nastavi na najblizsi
    temp_points = copy.deepcopy(points)

    for point in temp_points:
        min = float('inf')
        min_index = 0
        for i in range(0, len(centroids), 1):
            dist = distance(point, centroids[i])
            if(dist < min):
                min = dist
                min_index = i
        point.color = min_index
        point.distance_centroid = min
    return temp_points

def return_k_centroids(k,points):   # nahodna generacia centroidov pre k-means funkciu
    centroids = []
    body = copy.deepcopy(points)
    for i in range(k):
        a = random.choice(body)
        centroids.append(a)
        body.remove(a)

    return body, centroids

"""     algotitmy     """
def k_means_centroid(k, points):    # hlavna funckia k-means
    temp_points = copy.deepcopy(points)
    temp_points, temp_centroids = return_k_centroids(k,temp_points)

    gui(temp_centroids,temp_points)
    while(True):
        temp_points = assign_points_to_closest(temp_centroids, temp_points) # toto by mohlo byt normalne rychle
        what_next = recalculate_centroids(temp_centroids, temp_points)
        if(what_next == False):
            break

    gui(temp_centroids, temp_points)

    # vyhodnot chybne
    wrong = 0
    for i in temp_points:
        if (i.distance_centroid > 500):
            wrong += 1

    print(f"K-means so stredom centroide: (k={len(temp_centroids)})\nUspesnost: {(len(temp_points) - wrong) * 100 / len(temp_points)}")

########################################################
def find_smallest_distance(medoids, points): # najdi bod v klastri kotry ma najmensi sucet vzdialenosti ku vsetkym bodom a sprav z neho medoid
    # vycistim si hodnoty
    for i in medoids:
        i.distance_medoid = 0
    for i in points:
        i.distance_medoid = 0


    # vypocitam vsetky vzdialenosti
    for i in range(0, len(points), 1):
        dist1 = distance(points[i],medoids[points[i].color])
        points[i].distance_medoid += dist1
        medoids[points[i].color].distance_medoid += dist1
        for j in range(i+1,len(points),1):
            if (points[i].color == points[j].color):    # ak su z rovnakej farby
                dist = distance(points[i], points[j])
                points[i].distance_medoid += dist
                points[j].distance_medoid += dist

    # tu uz mam vsetky vzdialenosti spocitane
    zmena = False
    for i in range(0, len(points),1):
        if(points[i].distance_medoid < medoids[points[i].color].distance_medoid):   # prehodim ak som nasiel lepsieho kandidata na medoid
            temp1 = copy.deepcopy(points[i])
            points[i], medoids[temp1.color] = medoids[temp1.color], points[i]
            zmena = True

    return zmena


def give_random_points(points):     # vrat nahodny bod, pre inicializacne medoidy
    body = points.copy()
    medoids = []
    for i in range(CLUSTERS):
        aa = random.choice(body)
        body.remove(aa)
        medoids.append(aa)

    return medoids, body


def k_medoids(points):  # 2. halvny algoritmus
    temp_points = copy.deepcopy(points)
    temp_medoids, temp_points = give_random_points(temp_points)

    gui(temp_medoids, temp_points)

    while(True):
        temp_points = assign_points_to_closest(temp_medoids, temp_points)
        what = find_smallest_distance(temp_medoids, temp_points)
        if(what == False):
            break

    gui(temp_medoids, temp_points)


    # uspesnost
    middle_points = calculate_middle_of_clusters(len(temp_medoids),temp_points)

    wrong = 0

    for i in temp_points:
        dist = distance(i,middle_points[i.color])
        if(dist > 500):
            wrong += 1

    print(f"K-means so stredom medoid: (k={len(middle_points)})\nUspesnost: {(len(temp_points)-wrong)*100/len(temp_points)}")



#########################
# funkcia na vykreslenie plochy
def gui(centroids, points):
    colors = ["springgreen","green","blue", "yellow", "red", "brown", "purple", "pink", "lightgreen", "orange",
              "lightblue", "gold", "gray", "deeppink", "lime", "lightsalmon", "khaki", "navy", "firebrick", "tomato" , "sienna",
              "lightgray", "lightsalmon", "violet", "dodgerblue", "c"]
    plt.title("Zadanie 4 - Tomas Nemec")
    plt.xlabel('x - axis')
    plt.ylabel('y - axis')
    x_pos = []
    y_pos = []
    pos_colors = []
    for i in points:
        x_pos.append(i.x)
        y_pos.append(i.y)
        pos_colors.append(colors[i.color])

    plt.scatter(x_pos, y_pos, 1, color=pos_colors)

    if(centroids != None):
        x_pos_head = []
        y_pos_head = []
        for i in centroids:
            x_pos_head.append(i.x)
            y_pos_head.append(i.y)

        plt.scatter(x_pos_head, y_pos_head, 12, color="Black", marker="x")

    plt.show()
    return


"""     MAIN       """
#POINTS = 20000
#CLUSTERS = 25

CLUSTERS = int(input("Zadaj pocet klastrov: "))
POINTS = int(input("Zadaj pocet bodov: "))

base_20_points = is_unique(min_position,max_position,CLUSTERS)
main_points = generate_points(base_20_points, POINTS)

start = time.time()
k_means_centroid(CLUSTERS, main_points)
end = time.time()
print(f"Time: {end - start}")
print("======================================================================================================")



start1 = time.time()
k_medoids(main_points)
end1 = time.time()
print(f"Time: {end1 - start1}")
print("======================================================================================================")



