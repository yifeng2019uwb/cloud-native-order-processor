package main

import (
	"github.com/pulumi/pulumi-gcp/sdk/v9/go/gcp/container"
	"github.com/pulumi/pulumi-gcp/sdk/v9/go/gcp/serviceaccount"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {

		// service account
		sa, err := serviceaccount.NewAccount(ctx, serviceAccountID, &serviceaccount.AccountArgs{
			AccountId:   pulumi.String(serviceAccountID),
			DisplayName: pulumi.String("Order Processor Service Account"),
		})
		if err != nil {
			return err
		}

		// Artifact Registry repo + IAM
		if err = setupRegistry(ctx, sa); err != nil {
			return err
		}

		// GKE cluster — default node pool removed, Ubuntu node pools created separately
		cluster, err := container.NewCluster(ctx, clusterName, &container.ClusterArgs{
			Name:                  pulumi.String(clusterName),
			Location:              pulumi.String(zoneUsWest),
			RemoveDefaultNodePool: pulumi.Bool(true),
			InitialNodeCount:      pulumi.Int(1),
			DeletionProtection:    pulumi.Bool(false),
		})
		if err != nil {
			return err
		}

		// auth service node pool
		authPool, err := container.NewNodePool(ctx, svcAuth+"-pool", &container.NodePoolArgs{
			Name:     pulumi.String(svcAuth + "-pool"),
			Location: pulumi.String(zoneUsWest),
			Cluster:  cluster.Name,
			Autoscaling: &container.NodePoolAutoscalingArgs{
				MinNodeCount: pulumi.Int(1),
				MaxNodeCount: pulumi.Int(3),
			},
			NodeConfig: &container.NodePoolNodeConfigArgs{
				Preemptible:    pulumi.Bool(true),
				MachineType:    pulumi.String(machineType),
				ImageType:      pulumi.String(imageType),
				ServiceAccount: sa.Email,
				OauthScopes: pulumi.StringArray{
					pulumi.String(oauthScope),
				},
				Labels: pulumi.StringMap{
					"workload": pulumi.String(svcAuth),
				},
			},
		})
		if err != nil {
			return err
		}

		// export cluster name and auth pool name for kubectl usage
		ctx.Export("clusterName", cluster.Name)
		ctx.Export("clusterZone", pulumi.String(zoneUsWest))
		ctx.Export("authPoolName", authPool.Name)

		return nil
	})
}
