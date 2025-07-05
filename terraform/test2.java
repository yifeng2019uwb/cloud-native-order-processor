Array/String Manipulation
Problem 1: Given an array of integers, find all pairs of elements that sum to a specific target. Return the indices of all such pairs.
Problem 2: Given a string, find the longest substring that contains at most 2 distinct characters.
Problem 3: Rotate an array to the right by k steps. Modify the array in-place.
Problem 4: Given an array of strings, group anagrams together.
Two Pointers/Sliding Window
Problem 5: Given an array of positive integers and a target sum, find the minimum length of a contiguous subarray whose sum is greater than or equal to the target.
Problem 6: Given a string, find the length of the longest substring without repeating characters.
Problem 7: Given two sorted arrays, merge them into one sorted array.
Problem 8: Find all triplets in an array that sum to zero.
Hash Maps for Frequency Counting
Problem 9: Given two strings, determine if they are anagrams of each other.
Problem 10: Find the first non-repeating character in a string and return its index.
Problem 11: Given an array of integers, find the majority element (appears more than n/2 times).
Problem 12: Given an array, find all elements that appear more than n/3 times.
Basic Tree/Graph Traversal
Problem 13: Given a binary tree, return the level order traversal of its nodes' values.
Problem 14: Determine if a binary tree is a valid binary search tree.
Problem 15: Find the maximum depth of a binary tree.
Problem 16: Given a binary tree, find the lowest common ancestor of two given nodes.
Dynamic Programming (Simple)
Problem 17: You are climbing stairs. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. How many distinct ways can you climb to the top?
Problem 18: Given an array of non-negative integers representing the maximum number of steps you can make forward from each position, determine if you can reach the last index.
Problem 19: A robber is planning to rob houses along a street. Adjacent houses have security systems connected. Find the maximum amount of money the robber can rob without alerting the police.
Problem 20: Given a triangle array, return the minimum path sum from top to bottom.
Pick any problem number and I'll clarify constraints when you ask!


Problem 5: Given an array of positive integers and a target sum, find the minimum length of a contiguous subarray whose sum is greater than or equal to the target.

public int minimumLengthSubarray(int[] nums, int target) {
    if (nums == null || nums.length == 0) return -1; // edge case;
    int res = Integer.MAX_VALUE;

    int left = 0, sum = 0;

    for (int right = 0; right < nums.length; right++) {
        if (nums[right] >= target) return 1;
        sum += nums[right];
        if (sum < 0) {
            sum = 0;
            left = right + 1;
        }else {
            while (sum >= target) {
                if (right - left + 1 < res ) res = right - left + 1;
                sum -= nums[left++];
            }
        }

    }

    return res == Integer.MAX_VALUE? -1 : res;

}


Problem 6: Given a string, find the length of the longest substring without repeating characters.



public List<List<Integer>> getTriplets(int[] nums) {
    List<List<Integer>> res = new ArrayList<>();
    if (nums == null || nums.length < 3) return res;

    Arrays.sort(nums);

    for (int i = 0; i < nums.length - 2; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int left = i + 1, right = nums.length - 1;

        while (left < right) {
            int sum = nums[i] + nums[left] + nums[right] ;
            while (left < right && nums[left + 1] == nums[left]) left++;
            while (left <  right && nums[right - 1] == nums[right]) right--;

            if (sum == 0) {
                res.add(getList(nums[i], nums[left], nums[right]));
                left++;
                right--;
            }else if (sum < 0) {
                left++;
            }else {
                right--;
            }
        }
    }

    return res;
}

private List<Integer> getList(int a, int b, int c) {
    List<Integer> list = new ArrayList<>();
    list.add(a);
    list.add(b);
    list.add(c);
    return list;
}


Problem 10: Find the first non-repeating character in a string and return its index.

Basic Tree/Graph Traversal
Problem 13: Given a binary tree, return the level order traversal of its nodes' values.
    - BFS, Using Queue to retrieve the all node in same level/height

Problem 14: Determine if a binary tree is a valid binary search tree.
    - Retrieve Tree by pass min & max for each node, DFS, simple version of Leetcode 333

Problem 15: Find the maximum depth of a binary tree.
    - DFS, return maximum depth of left and right subtree + 1;

Problem 16: Given a binary tree, find the lowest common ancestor of two given nodes.
    - Find the p1, p2 if in the left subtree and right subTree, compare to get the result.

All TC: O(N) 

Will to quick code for all!


Problem 13: Given a binary tree, return the level order traversal of its nodes' values.
public List<List<Integer>> getTree(TreeNode root) {
    List<List<Integer>> res = new ArrayList<>();
    if (root == null) return res;

    Queue<TreeNode> qu = new LinkedList<>();
    qu.offer(root);

    while (!qu.isEmpty()) {
        List<Integer> list = new ArrayList<>();
        int size = qu.size(); // all node in cur level
        for (int i = 0; i < size; i++) {
            TreeNode node = qu.poll();
            list.add(node.val);
            if (node.left != null) qu.offer(node.left);
            if (node.right != null) qu.offer(node.right);
        }
        res.add(list);// Can be reverse if need for zigzag et cases.
    }
    return res;
}


Problem 14: Determine if a binary tree is a valid binary search tree.

public boolean isBST(TreeNode root) {
    if (root == null) return true;
    return isBSTHelper(root, Integer.MIN_VALUE, Integer.MAX_VALUE);

}

// min and max may be long due to root.val range
private boolean isBSTHelper(TreeNode root, int min, int max) {
    if (root == null) return true;
    if (root.val <= min || root.val >= max) return false; // left node value may be same as parent node val, for constrains requirement
    boolean leftBST = isBSTHelper(root.left, min, root.val);
    if (!leftBST) return false;
    boolean rightBST = isBSTHelper(root.right, root.val, max);
    return rightBST;
}


Problem 15: Find the maximum depth of a binary tree.
public int getTreeHeight(TreeNode root) {
    if (root == null) return 0;
    return Math.max(getTreeHeight(root.left), getTreeHeight(root.right)) + 1;
}    
    

public TreeNode getLowestCommonAncestor(TreeNode root, TreeNode p1, TreeNode p2) {
    if (root == null || root == p1 || root == p2) return root;
    
    TreeNode left = getLowestCommonAncestor(root.left, p1, p2);
    TreeNode right = getLowestCommonAncestor(root.right, p1, p2);
    
    if (left != null && right != null) return root;  // p1 and p2 in different subtrees
    return left != null ? left : right;  // Both in same subtree
}


Problem 16: Given a binary tree, find the lowest common ancestor of two given nodes.
    
public TreeNode getLowestCommonAncestor(TreeNode root, TreeNode p1, TreeNode p2) {
    if (root == null || p1 == null || p2 == null) return null;
    if (root == p1) return p1;
    if (root == p2) return p2;
    boolean l1 = findNode(root.left, p1);
    boolean r1 = findNode(root.right, p1);
    boolean l2 = findNode(root.left, p2);
    boolean r2 = findNode(root.right, p2);
    if ( (l1 && r2) || (r1 && l2)) return root;
    if (l1 && l2) return getLowestCommonAncestor(root.left, p1, p2);
    if (r1 && r2) return getLowestCommonAncestor(root.right, p1, p2);
    return null;
}

private boolean findNode(TreeNode root, TreeNode p) {
    if (root == null || p == null) return false;
    if (root == p) return true;
    return findNode(root.left, p) || findNode(root.right, p);
}



public TreeNode getLowestCommonAncestor(TreeNode root, TreeNode p1, TreeNode p2) {
    if (root == null || root == p1 || root == p2) return root;
    
    // I actually confused here
    TreeNode left = getLowestCommonAncestor(root.left, p1, p2);
    TreeNode right = getLowestCommonAncestor(root.right, p1, p2);
    
    // if left != null, means lowestCommonAncestor in left sub stree, the answer is left
    // same for right != null;
    // both left and right cannot be null at same time;
    if (left != null && right != null) return root;  // p1 and p2 in different subtrees
    return left != null ? left : right;  // Both in same subtree
}


Problem 17: You are climbing stairs. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. How many distinct ways can you climb to the top?
Problem 18: Given an array of non-negative integers representing the maximum number of steps you can make forward from each position, determine if you can reach the last index.
Problem 19: A robber is planning to rob houses along a street. Adjacent houses have security systems connected. Find the maximum amount of money the robber can rob without alerting the police.
Problem 20: Given a triangle array, return the minimum path sum from top to bottom.


Problem 17: You are climbing stairs. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. How many distinct ways can you climb to the top?
// suppose stairs are always non-negative? 
// what's stairs range?


// this case for 1 <= n <= 45, answer in interger round
public int solution(int n) {
    int[] arr = new int[n + 1];
    arr[0] = 1;
    arr[1] = 1;

    for (int i = 2; i <= n; i++) {
        arr[i] = arr[i - 1] + arr[i - 2];
    }
    return arr[n];
}

arr: {1,1, 2, 3, 5, 8...} 
        1, 2, 3, 5,
// this case n is large num, but always positive;
public long solution(int n) {
    long n0 = 1l, n1 = 1l, n2 = 1l;

    while (n-- > 1) {
        n2 = n0 + n1;
        n0 = n1;
        n1 = n2;
    }
    return n2;
}

n = 1 => return n2 = 1;
n = 2 => n2 = 1 + 1= 2, n1 = 2, n0 = 1; => return n2 = 2;
n = 3 => n2 = 2+1= 3, n1 = 3, n0 = 2; => return n2 = 2;
n = 4 => n2 = 3+2 =5, n1 = 5, n0 = 3; => n2 = 5;

Problem 18: Given an array of non-negative integers representing the maximum number of steps you can make forward from each position, determine if you can reach the last index.
Retrieve the arr to update maximum steps can reach, stop when maximum is out of array range or no more steps can go;

public int getMaxSteps(int[] nums) {
    if (nums == null || nums.length == 0) return 0;
    int res = 0, curIdx = 0;

    while (curIdx <= res && curIdx < nums.length) {
        if (curIdx + nums[curIdx] > res) {
            res = curIdx + nums[curIdx];
            if (res >= nums.length) break; // nums.length is out of range, nums.length - 1 is still in range;
            curIdx++;
        }

    }

    return res >= nums.length? nums.length : res;
}


Problem 19: A robber is planning to rob houses along a street. Adjacent houses have security systems connected. Find the maximum amount of money the robber can rob without alerting the police.
Using an array to update the maximum money the robber can get until the home by order. 

public int getMaxMoney(int[] houses) {
    int n = houses.length;
    if (house == null || house.length == 0) return 0;
    if (houses.length == 1) return houses[0];

    int[] dp = new int[n+ 1];
    dp[1] = houses[0];

    for (int i = 1; i < houses.length; i++) {
        dp[i + 1] = Math.max(dp[i], dp[i - 1] + houses[i]);
    }

    return Math.max(dp[n], dp[n - 1]);
}

// if the first and last home are also connect, Will try to retrieve twice of house by start from house 0 and house 1, for start from house 0, skip the last house, compare dp[n - 2], dp[n - 1], for house1, compare dp[n], dp[n - 1].final answer from compare all 4 values. But only need one dp to recor all;


Problem 20: Given a triangle array, return the minimum path sum from top to bottom.

// may use int[][] as input
public int getMinPathValue(List<List<Integer>> lists) {
    if (lists == null || lists.size() == 0) return 0; // edge case
    int n = lists.size();
    // update the array in each layer with minimum path sum;

    for (int i = 1; i < n; i++) {
        // size of cur array > 2;
        lists.get(i).set(0, lists.get(i - 1).get(0) + lists.get(i).get(0));
        for (int j = 1; j < i; j++) {
            lists.get(i).set(j, Math.min(lists.get(i - 1).(j - 1), lists.get(i - 1).get(j)) + lists.get(i).get(j));
        }
        lists.get(i).set(i, lists.get(i - 1).get(i - 1) + lists.get(i).get(i));
    }

    List<Integer> lastLine = lists.get(n - 1);
    int min = lastLine.get(0);

    for (int i = 1; i < n; i++) {
        if (lastLine.get(i) < min) min = lastLine.get(i);
    }
    return min;
}


aaabbb

ab + 1 or more

2 + 2;
4 + 3 + 2 +1 = 8;

abcd; extra = 1 + 1 + 1 + 1 = 4; 
need pick 3;

but combination are diff