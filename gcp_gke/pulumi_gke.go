package main

import (
	"github.com/pulumi/pulumi-gcp/sdk/v9/go/gcp/container"
	"github.com/pulumi/pulumi-gcp/sdk/v9/go/gcp/serviceaccount"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func setupServiceAccount(ctx *pulumi.Context) (*serviceaccount.Account, error) {
	return serviceaccount.NewAccount(ctx, serviceAccountID, &serviceaccount.AccountArgs{
		AccountId:   pulumi.String(serviceAccountID),
		DisplayName: pulumi.String("Order Processor Service Account"),
	})
}

func deployCluster(ctx *pulumi.Context, sa *serviceaccount.Account, cfg ClusterConfig) error {
	cluster, err := container.NewCluster(ctx, cfg.Name, &container.ClusterArgs{
		Name:                  pulumi.String(cfg.Name),
		Location:              pulumi.String(cfg.Zone),
		RemoveDefaultNodePool: pulumi.Bool(true),
		InitialNodeCount:      pulumi.Int(1),
		DeletionProtection:    pulumi.Bool(false),
	})
	if err != nil {
		return err
	}

	authPool, err := container.NewNodePool(ctx, cfg.Name+"-"+svcAuth+"-pool", &container.NodePoolArgs{
		Name:     pulumi.String(svcAuth + "-pool"),
		Location: pulumi.String(cfg.Zone),
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

	ctx.Export("clusterName-"+cfg.Region, cluster.Name)
	ctx.Export("clusterZone-"+cfg.Region, pulumi.String(cfg.Zone))
	ctx.Export("authPoolName-"+cfg.Region, authPool.Name)

	return nil
}
